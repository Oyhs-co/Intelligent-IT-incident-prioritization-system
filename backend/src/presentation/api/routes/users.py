"""Rutas de usuarios."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.application.use_cases.users import (
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserUseCase,
)
from src.domain.entities.user import User
from src.infrastructure.database import get_db_session
from src.infrastructure.database.repositories import UserRepository
from src.presentation.schemas import (
    UpdateUserRequest,
    UserListResponse,
    UserResponse,
)

from .dependencies import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


def _user_to_response(user: User) -> UserResponse:
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


@router.get("/", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: str | None = None,
    is_active: bool | None = None,
    session=Depends(get_db_session),
    current_user: dict | None = Depends(get_current_user),
):
    """Lista usuarios del sistema."""
    user_repo = UserRepository(session)
    use_case = ListUsersUseCase(user_repo)

    result = await use_case.execute(
        skip=skip,
        limit=limit,
        role=role,
        is_active=is_active,
    )

    return UserListResponse(
        items=[_user_to_response(u) for u in result.items],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    session=Depends(get_db_session),
    current_user: dict | None = Depends(get_current_user),
):
    """Obtiene un usuario por su ID."""
    user_repo = UserRepository(session)
    use_case = GetUserUseCase(user_repo)

    try:
        user = await use_case.execute(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        ) from e

    return _user_to_response(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
    session=Depends(get_db_session),
    current_user: dict | None = Depends(get_current_user),
):
    """Actualiza un usuario."""
    from src.domain.entities.user import UserRole

    user_repo = UserRepository(session)
    use_case = UpdateUserUseCase(user_repo)

    from src.application.use_cases.users.update_user import (
        UpdateUserRequest as UpdateUserReq,
    )

    req = UpdateUserReq(
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        department=request.department,
        role=UserRole(request.role) if request.role else None,
        is_active=request.is_active,
    )

    try:
        user = await use_case.execute(user_id, req)
        await session.commit()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        ) from e

    return _user_to_response(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    session=Depends(get_db_session),
    current_user: dict | None = Depends(get_current_user),
):
    """Elimina un usuario."""
    user_repo = UserRepository(session)

    deleted = await user_repo.delete(user_id)
    await session.commit()

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )

    return None
