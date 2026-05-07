"""Servicio de autenticación."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
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
    """Datos del token JWT."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800


@dataclass
class AuthResult:
    """Resultado de autenticación exitosa."""

    user: User
    tokens: TokenData


class AuthService:
    """Servicio de autenticación y autorización."""

    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15

    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository

    def _hash_password(self, password: str) -> str:
        """Hashea una contraseña usando bcrypt."""
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def _create_access_token(
        self,
        user_id: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Crea un token de acceso JWT."""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.access_token_expire_minutes,
            )

        to_encode = {
            "sub": user_id,
            "exp": expire,
            "type": "access",
        }
        return jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm,
        )

    def _create_refresh_token(self, user_id: str) -> str:
        """Crea un token de refresh JWT."""
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days,
        )
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "type": "refresh",
        }
        return jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm,
        )

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
        """Registra un nuevo usuario.

        Args:
            email: Email del usuario
            username: Nombre de usuario
            password: Contraseña sin hashear
            first_name: Nombre
            last_name: Apellido
            department: Departamento
            role: Rol del usuario

        Returns:
            Usuario creado

        Raises:
            ValueError: Si el email o username ya existen
        """
        existing_email = await self._user_repo.get_by_email(email)
        if existing_email:
            logger.warning(
                "Registro fallido: email duplicado",
                email=email,
            )
            raise ValueError("Email already registered")

        existing_username = await self._user_repo.get_by_username(username)
        if existing_username:
            logger.warning(
                "Registro fallido: username duplicado",
                username=username,
            )
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

        logger.info(
            "Usuario registrado exitosamente",
            email=email,
            user_id=str(created_user.id),
            role=role.value,
        )

        return created_user

    async def authenticate(self, email: str, password: str) -> AuthResult:
        """Autentica un usuario por email y contraseña.

        Args:
            email: Email del usuario
            password: Contraseña

        Returns:
            Resultado con usuario y tokens

        Raises:
            AuthenticationException: Si credenciales inválidas o usuario inactivo
        """
        user = await self._user_repo.get_by_email(email)
        if not user:
            logger.warning(
                "Autenticación fallida: usuario no encontrado",
                email=email,
            )
            raise AuthenticationException("Invalid credentials")

        if not user.is_active:
            logger.warning(
                "Autenticación fallida: usuario inactivo",
                email=email,
                user_id=str(user.id),
            )
            raise AuthenticationException("User account is disabled")

        if not user.verify_password(password):
            logger.warning(
                "Autenticación fallida: contraseña incorrecta",
                email=email,
                user_id=str(user.id),
            )
            raise AuthenticationException("Invalid credentials")

        user.record_login()
        await self._user_repo.update(user)

        access_token = self._create_access_token(str(user.id))
        refresh_token = self._create_refresh_token(str(user.id))

        logger.info(
            "Usuario autenticado exitosamente",
            email=email,
            user_id=str(user.id),
        )

        return AuthResult(
            user=user,
            tokens=TokenData(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.access_token_expire_minutes * 60,
            ),
        )

    async def verify_token(self, token: str) -> Optional[str]:
        """Verifica un token JWT y retorna el user_id.

        Args:
            token: Token JWT de acceso

        Returns:
            user_id como string, o None si el token es inválido
        """
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm],
            )
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")

            if user_id is None or token_type != "access":
                return None

            return user_id

        except JWTError as e:
            logger.warning(
                "Verificación de token fallida",
                error=str(e),
            )
            return None

    async def refresh_access_token(self, refresh_token: str) -> TokenData:
        """Refresca un token de acceso usando un refresh token.

        Args:
            refresh_token: Token JWT de refresh

        Returns:
            Nuevos datos de token

        Raises:
            AuthenticationException: Si el refresh token es inválido
        """
        try:
            payload = jwt.decode(
                refresh_token,
                settings.secret_key,
                algorithms=[settings.algorithm],
            )
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")

            if user_id is None or token_type != "refresh":
                raise AuthenticationException("Invalid refresh token")

            user = await self._user_repo.get_by_id(UUID(user_id))
            if not user or not user.is_active:
                raise AuthenticationException("User not found or inactive")

            new_access_token = self._create_access_token(user_id)

            logger.info(
                "Token de acceso refrescado",
                user_id=user_id,
            )

            return TokenData(
                access_token=new_access_token,
                refresh_token=refresh_token,
                expires_in=settings.access_token_expire_minutes * 60,
            )

        except JWTError as e:
            logger.warning(
                "Refresh token inválido",
                error=str(e),
            )
            raise AuthenticationException("Invalid refresh token")

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Obtiene un usuario por su ID.

        Args:
            user_id: UUID del usuario

        Returns:
            Usuario o None si no existe
        """
        return await self._user_repo.get_by_id(user_id)
