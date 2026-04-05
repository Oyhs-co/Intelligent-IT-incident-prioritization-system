"""Servicio de autenticación."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.domain.entities.user import User, UserRole
from src.domain.repositories import IUserRepository
from src.shared.config import get_settings
from src.shared.logging import get_logger
from src.shared.exceptions import AuthenticationException

if TYPE_CHECKING:
    pass

settings = get_settings()
logger = get_logger("auth_service")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class TokenData:
    """Datos del token."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800


@dataclass
class AuthResult:
    """Resultado de autenticación."""

    user: User
    tokens: TokenData


class AuthService:
    """Servicio de autenticación y autorización."""

    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository

    def _hash_password(self, password: str) -> str:
        """Hashea una contraseña."""
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña."""
        return pwd_context.verify(plain_password, hashed_password)

    def _create_access_token(self, user_id: str, expires_delta: Optional[timedelta] = None) -> str:
        """Crea un token de acceso."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

        to_encode = {
            "sub": user_id,
            "exp": expire,
            "type": "access",
        }
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    def _create_refresh_token(self, user_id: str) -> str:
        """Crea un token de refresh."""
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "type": "refresh",
        }
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    async def register_user(
        self,
        email: str,
        username: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        department: Optional[str] = None,
        role: UserRole = UserRole.USER,
    ) -> User:
        """Registra un nuevo usuario."""
        existing_email = await self._user_repo.get_by_email(email)
        if existing_email:
            raise ValueError("Email already registered")

        existing_username = await self._user_repo.get_by_username(username)
        if existing_username:
            raise ValueError("Username already taken")

        user = User()
        user.email = email
        user.username = username
        user.set_password(password)
        user.role = role
        user.first_name = first_name
        user.last_name = last_name
        user.department = department
        user.is_verified = True

        created_user = await self._user_repo.create(user)

        logger.info(f"User registered: {email}", user_id=str(created_user.id))

        return created_user

    async def authenticate(self, email: str, password: str) -> AuthResult:
        """Autentica un usuario."""
        user = await self._user_repo.get_by_email(email)
        if not user:
            logger.warning(f"Login failed: user not found {email}")
            raise AuthenticationException("Invalid credentials")

        if not user.is_active:
            logger.warning(f"Login failed: user inactive {email}")
            raise AuthenticationException("User account is disabled")

        if not self._verify_password(password, user._hashed_password):
            logger.warning(f"Login failed: invalid password {email}")
            raise AuthenticationException("Invalid credentials")

        user.record_login()
        await self._user_repo.update(user)

        access_token = self._create_access_token(str(user.id))
        refresh_token = self._create_refresh_token(str(user.id))

        logger.info(f"User authenticated: {email}", user_id=str(user.id))

        return AuthResult(
            user=user,
            tokens=TokenData(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.access_token_expire_minutes * 60,
            ),
        )

    async def verify_token(self, token: str) -> Optional[str]:
        """Verifica un token y retorna el user_id."""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")

            if user_id is None or token_type != "access":
                return None

            return user_id

        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None

    async def refresh_access_token(self, refresh_token: str) -> TokenData:
        """Refresca un token de acceso."""
        try:
            payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")

            if user_id is None or token_type != "refresh":
                raise AuthenticationException("Invalid refresh token")

            user = await self._user_repo.get_by_id(UUID(user_id))
            if not user or not user.is_active:
                raise AuthenticationException("User not found or inactive")

            new_access_token = self._create_access_token(user_id)

            return TokenData(
                access_token=new_access_token,
                refresh_token=refresh_token,
                expires_in=settings.access_token_expire_minutes * 60,
            )

        except JWTError as e:
            logger.warning(f"Refresh token verification failed: {e}")
            raise AuthenticationException("Invalid refresh token")

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Obtiene un usuario por su ID."""
        return await self._user_repo.get_by_id(user_id)
