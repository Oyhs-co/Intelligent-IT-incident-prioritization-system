"""Schemas Pydantic para autenticación."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request para registrar usuario."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    first_name: str = Field(default="", max_length=100)
    last_name: str = Field(default="", max_length=100)
    department: Optional[str] = None


class LoginRequest(BaseModel):
    """Request para login."""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Request para refrescar token."""

    refresh_token: str


class TokenResponse(BaseModel):
    """Response de token."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """Response de usuario."""

    model_config = {"from_attributes": True}

    id: UUID
    email: str
    username: str
    role: str
    first_name: str
    last_name: str
    full_name: str
    department: Optional[str] = None
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    created_at: datetime
