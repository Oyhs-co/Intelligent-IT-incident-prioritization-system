"""Rutas de autenticación."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from src.application.services import AuthService
from src.infrastructure.database.repositories import UserRepository
from src.infrastructure.database import get_db_session
from src.presentation.schemas import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Registra un nuevo usuario."""
    async for session in get_db_session():
        user_repo = UserRepository(session)
        auth_service = AuthService(user_repo)

        try:
            user = await auth_service.register_user(
                email=request.email,
                username=request.username,
                password=request.password,
                first_name=request.first_name,
                last_name=request.last_name,
                department=request.department,
            )
            await session.commit()

            return UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                role=user.role.value,
                first_name=user.first_name,
                last_name=user.last_name,
                full_name=user.full_name,
                department=user.department,
                is_active=user.is_active,
                is_verified=user.is_verified,
                last_login=user.last_login,
                created_at=user.created_at,
            )

        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Inicia sesión."""
    async for session in get_db_session():
        user_repo = UserRepository(session)
        auth_service = AuthService(user_repo)

        try:
            result = await auth_service.authenticate(request.email, request.password)
            await session.commit()

            return TokenResponse(
                access_token=result.tokens.access_token,
                refresh_token=result.tokens.refresh_token,
                token_type=result.tokens.token_type,
                expires_in=result.tokens.expires_in,
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Refresca el token de acceso."""
    async for session in get_db_session():
        user_repo = UserRepository(session)
        auth_service = AuthService(user_repo)

        try:
            tokens = await auth_service.refresh_access_token(request.refresh_token)

            return TokenResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                token_type=tokens.token_type,
                expires_in=tokens.expires_in,
            )

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(__import__("routes.dependencies", fromlist=["get_current_user"]).get_current_user),
):
    """Obtiene información del usuario actual."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    async for session in get_db_session():
        user_repo = UserRepository(session)
        auth_service = AuthService(user_repo)

        from uuid import UUID
        user = await auth_service.get_user_by_id(UUID(current_user["id"]))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            role=user.role.value,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            department=user.department,
            is_active=user.is_active,
            is_verified=user.is_verified,
            last_login=user.last_login,
            created_at=user.created_at,
        )
