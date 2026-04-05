"""Entidad User con encapsulamiento completo."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from passlib.context import CryptContext

from .base import BaseEntity


class UserRole(Enum):
    """Roles de usuario en el sistema."""

    ADMIN = "admin"
    TECHNICIAN = "technician"
    USER = "user"
    VIEWER = "viewer"

    @property
    def can_assign_incidents(self) -> bool:
        """Verifica si el rol puede asignar incidentes."""
        return self in (UserRole.ADMIN, UserRole.TECHNICIAN)

    @property
    def can_resolve_incidents(self) -> bool:
        """Verifica si el rol puede resolver incidentes."""
        return self in (UserRole.ADMIN, UserRole.TECHNICIAN)

    @property
    def can_manage_users(self) -> bool:
        """Verifica si el rol puede gestionar usuarios."""
        return self == UserRole.ADMIN


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class User(BaseEntity):
    """Entidad User con encapsulamiento completo."""

    _email: str = field(default="")
    _username: str = field(default="")
    _hashed_password: str = field(default="")
    _role: UserRole = field(default=UserRole.USER)
    _first_name: str = field(default="")
    _last_name: str = field(default="")
    _department: Optional[str] = field(default=None)
    _is_active: bool = field(default=True)
    _is_verified: bool = field(default=False)
    _last_login: Optional[datetime] = field(default=None)

    @property
    def email(self) -> str:
        """Obtiene el email del usuario."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        """Establece el email del usuario."""
        value = value.lower().strip()
        if "@" not in value:
            raise ValueError("Invalid email format")
        object.__setattr__(self, "_email", value)
        self._mark_updated()

    @property
    def username(self) -> str:
        """Obtiene el nombre de usuario."""
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        """Establece el nombre de usuario."""
        value = value.strip().lower()
        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters")
        object.__setattr__(self, "_username", value)
        self._mark_updated()

    @property
    def role(self) -> UserRole:
        """Obtiene el rol del usuario."""
        return self._role

    @role.setter
    def role(self, value: UserRole) -> None:
        """Establece el rol del usuario."""
        object.__setattr__(self, "_role", value)
        self._mark_updated()

    @property
    def first_name(self) -> str:
        """Obtiene el nombre."""
        return self._first_name

    @first_name.setter
    def first_name(self, value: str) -> None:
        """Establece el nombre."""
        object.__setattr__(self, "_first_name", value.strip())
        self._mark_updated()

    @property
    def last_name(self) -> str:
        """Obtiene el apellido."""
        return self._last_name

    @last_name.setter
    def last_name(self, value: str) -> None:
        """Establece el apellido."""
        object.__setattr__(self, "_last_name", value.strip())
        self._mark_updated()

    @property
    def full_name(self) -> str:
        """Obtiene el nombre completo."""
        return f"{self._first_name} {self._last_name}".strip()

    @property
    def department(self) -> Optional[str]:
        """Obtiene el departamento."""
        return self._department

    @department.setter
    def department(self, value: Optional[str]) -> None:
        """Establece el departamento."""
        object.__setattr__(self, "_department", value)
        self._mark_updated()

    @property
    def is_active(self) -> bool:
        """Verifica si el usuario está activo."""
        return self._is_active

    @is_active.setter
    def is_active(self, value: bool) -> None:
        """Activa o desactiva el usuario."""
        object.__setattr__(self, "_is_active", value)
        self._mark_updated()

    @property
    def is_verified(self) -> bool:
        """Verifica si el usuario está verificado."""
        return self._is_verified

    @is_verified.setter
    def is_verified(self, value: bool) -> None:
        """Establece la verificación del usuario."""
        object.__setattr__(self, "_is_verified", value)
        self._mark_updated()

    @property
    def last_login(self) -> Optional[datetime]:
        """Obtiene la última fecha de login."""
        return self._last_login

    def set_password(self, password: str) -> None:
        """Establece la contraseña hasheada."""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        object.__setattr__(self, "_hashed_password", pwd_context.hash(password))
        self._mark_updated()

    def verify_password(self, password: str) -> bool:
        """Verifica la contraseña."""
        return pwd_context.verify(password, self._hashed_password)

    def record_login(self) -> None:
        """Registra un nuevo login."""
        object.__setattr__(self, "_last_login", datetime.utcnow())
        self._mark_updated()

    def to_dict(self) -> dict[str, Any]:
        """Convierte la entidad a diccionario."""
        return {
            **super().to_dict(),
            "email": self._email,
            "username": self._username,
            "role": self._role.value,
            "first_name": self._first_name,
            "last_name": self._last_name,
            "full_name": self.full_name,
            "department": self._department,
            "is_active": self._is_active,
            "is_verified": self._is_verified,
            "last_login": self._last_login.isoformat() if self._last_login else None,
        }
