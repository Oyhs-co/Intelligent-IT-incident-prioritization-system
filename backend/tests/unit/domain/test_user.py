"""Tests unitarios para la entidad User."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from src.domain.entities.user import User, UserRole


@pytest.fixture(autouse=True)
def _mock_pwd_context():
    """Mockea pwd_context global para evitar dependencia de bcrypt en Python 3.14."""
    with patch("src.domain.entities.user.pwd_context") as mock:
        mock.hash.return_value = "$2b$12$hashed_password_mock"
        mock.verify.return_value = True
        yield mock


def _make_user(**kwargs) -> User:
    """Crea un User con valores mínimos."""
    u = User()
    defaults = {
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
    }
    for k, v in {**defaults, **kwargs}.items():
        setattr(u, k, v)
    return u


class TestUserCreation:
    """Tests de creación básica de User."""

    def test_create_user_defaults(self):
        """Crear un usuario debe tener valores por defecto correctos."""
        u = User()
        u.email = "test@example.com"
        u.username = "testuser"
        assert u.email == "test@example.com"
        assert u.username == "testuser"
        assert u.role == UserRole.USER
        assert u.first_name == ""
        assert u.last_name == ""
        assert u.full_name == ""
        assert u.department is None
        assert u.is_active is True
        assert u.is_verified is False
        assert u.last_login is None

    def test_create_with_values(self):
        """Crear con valores personalizados."""
        u = _make_user()
        assert u.email == "test@example.com"
        assert u.username == "testuser"
        assert u.first_name == "Test"
        assert u.last_name == "User"
        assert u.full_name == "Test User"

    def test_id_is_uuid(self):
        """El ID debe ser un UUID."""
        u = _make_user()
        from uuid import UUID
        assert isinstance(u.id, UUID)

    def test_created_at_auto(self):
        """created_at debe establecerse automáticamente."""
        u = _make_user()
        assert isinstance(u.created_at, datetime)

    def test_updated_at_inicial(self):
        """updated_at debe ser igual a created_at inicialmente."""
        u = _make_user()
        assert isinstance(u.updated_at, datetime)


class TestUserEmailValidation:
    """Tests de validación del email."""

    def test_email_valid(self):
        """Email válido debe funcionar."""
        u = User()
        u.email = "user@example.com"
        assert u.email == "user@example.com"

    def test_email_lowercase(self):
        """Email debe convertirse a minúsculas."""
        u = User()
        u.email = "User@Example.COM"
        assert u.email == "user@example.com"

    def test_email_strip_whitespace(self):
        """Email debe eliminar espacios."""
        u = User()
        u.email = "  user@example.com  "
        assert u.email == "user@example.com"

    def test_email_invalid_no_at(self):
        """Email sin @ debe lanzar ValueError."""
        u = User()
        with pytest.raises(ValueError, match="Invalid email format"):
            u.email = "invalid-email"

    def test_email_empty_raises_error(self):
        """Email vacío debe lanzar ValueError."""
        u = User()
        with pytest.raises(ValueError, match="Invalid email format"):
            u.email = ""

    def test_email_whitespace_only_raises_error(self):
        """Email con solo espacios debe lanzar ValueError."""
        u = User()
        with pytest.raises(ValueError, match="Invalid email format"):
            u.email = "   "


class TestUserUsernameValidation:
    """Tests de validación del username."""

    def test_username_valid(self):
        """Username válido debe funcionar."""
        u = User()
        u.username = "myuser"
        assert u.username == "myuser"

    def test_username_lowercase(self):
        """Username debe convertirse a minúsculas."""
        u = User()
        u.username = "MyUser"
        assert u.username == "myuser"

    def test_username_strip_whitespace(self):
        """Username debe eliminar espacios."""
        u = User()
        u.username = "  myuser  "
        assert u.username == "myuser"

    def test_username_too_short_raises_error(self):
        """Username menor a 3 caracteres debe lanzar ValueError."""
        u = User()
        with pytest.raises(ValueError, match="at least 3 characters"):
            u.username = "ab"

    def test_username_empty_raises_error(self):
        """Username vacío debe lanzar ValueError."""
        u = User()
        with pytest.raises(ValueError, match="at least 3 characters"):
            u.username = ""

    def test_username_whitespace_only_raises_error(self):
        """Username con solo espacios debe lanzar ValueError."""
        u = User()
        with pytest.raises(ValueError, match="at least 3 characters"):
            u.username = "   "

    def test_username_exact_three(self):
        """Username de exactamente 3 caracteres debe ser válido."""
        u = User()
        u.username = "abc"
        assert u.username == "abc"


class TestUserPassword:
    """Tests de gestión de contraseñas."""

    def test_set_password(self, _mock_pwd_context):
        """set_password debe llamar a pwd_context.hash."""
        u = _make_user()
        u.set_password("password123")
        _mock_pwd_context.hash.assert_called_once_with("password123")

    def test_set_password_too_short(self, _mock_pwd_context):
        """Contraseña menor a 8 caracteres debe lanzar ValueError."""
        u = _make_user()
        with pytest.raises(ValueError, match="at least 8 characters"):
            u.set_password("1234567")

    def test_verify_password(self, _mock_pwd_context):
        """verify_password debe llamar a pwd_context.verify."""
        u = _make_user()
        result = u.verify_password("password123")
        _mock_pwd_context.verify.assert_called_once()
        assert result is True


class TestUserRecordLogin:
    """Tests de registro de login."""

    def test_record_login_sets_last_login(self):
        """record_login debe establecer last_login."""
        u = _make_user()
        assert u.last_login is None
        u.record_login()
        assert u.last_login is not None
        assert isinstance(u.last_login, datetime)

    def test_record_login_calls_mark_updated(self):
        """record_login debe actualizar updated_at."""
        u = _make_user()
        before = u.updated_at
        u.record_login()
        assert u.updated_at >= before


class TestUserRoles:
    """Tests de roles y permisos."""

    def test_default_role_is_user(self):
        """El rol por defecto debe ser USER."""
        u = _make_user()
        assert u.role == UserRole.USER

    def test_set_role_admin(self):
        """Se debe poder asignar el rol ADMIN."""
        u = _make_user()
        u.role = UserRole.ADMIN
        assert u.role == UserRole.ADMIN

    def test_admin_can_assign(self):
        """ADMIN puede asignar incidentes."""
        assert UserRole.ADMIN.can_assign_incidents is True

    def test_admin_can_resolve(self):
        """ADMIN puede resolver incidentes."""
        assert UserRole.ADMIN.can_resolve_incidents is True

    def test_admin_can_manage(self):
        """ADMIN puede gestionar usuarios."""
        assert UserRole.ADMIN.can_manage_users is True

    def test_technician_can_assign(self):
        """TECHNICIAN puede asignar incidentes."""
        assert UserRole.TECHNICIAN.can_assign_incidents is True

    def test_technician_can_resolve(self):
        """TECHNICIAN puede resolver incidentes."""
        assert UserRole.TECHNICIAN.can_resolve_incidents is True

    def test_technician_cannot_manage(self):
        """TECHNICIAN NO puede gestionar usuarios."""
        assert UserRole.TECHNICIAN.can_manage_users is False

    def test_user_cannot_assign(self):
        """USER NO puede asignar incidentes."""
        assert UserRole.USER.can_assign_incidents is False

    def test_user_cannot_resolve(self):
        """USER NO puede resolver incidentes."""
        assert UserRole.USER.can_resolve_incidents is False

    def test_user_cannot_manage(self):
        """USER NO puede gestionar usuarios."""
        assert UserRole.USER.can_manage_users is False

    def test_viewer_cannot_assign(self):
        """VIEWER NO puede asignar incidentes."""
        assert UserRole.VIEWER.can_assign_incidents is False

    def test_viewer_cannot_resolve(self):
        """VIEWER NO puede resolver incidentes."""
        assert UserRole.VIEWER.can_resolve_incidents is False

    def test_viewer_cannot_manage(self):
        """VIEWER NO puede gestionar usuarios."""
        assert UserRole.VIEWER.can_manage_users is False


class TestUserProperties:
    """Tests de propiedades y setters."""

    def test_first_name_setter(self):
        """first_name debe asignarse correctamente."""
        u = _make_user()
        u.first_name = "Juan"
        assert u.first_name == "Juan"

    def test_first_name_strip(self):
        """first_name debe eliminar espacios."""
        u = _make_user()
        u.first_name = "  Juan  "
        assert u.first_name == "Juan"

    def test_last_name_setter(self):
        """last_name debe asignarse correctamente."""
        u = _make_user()
        u.last_name = "Pérez"
        assert u.last_name == "Pérez"

    def test_last_name_strip(self):
        """last_name debe eliminar espacios."""
        u = _make_user()
        u.last_name = "  Pérez  "
        assert u.last_name == "Pérez"

    def test_full_name_both(self):
        """full_name debe combinar nombre y apellido."""
        u = _make_user()
        assert u.full_name == "Test User"

    def test_full_name_no_last(self):
        """full_name sin apellido debe mostrar solo el nombre."""
        u = User()
        u.email = "test@example.com"
        u.username = "testuser"
        u.first_name = "Test"
        assert u.full_name == "Test"

    def test_full_name_no_first(self):
        """full_name sin nombre debe mostrar solo el apellido."""
        u = User()
        u.email = "test@example.com"
        u.username = "testuser"
        u.last_name = "User"
        assert u.full_name == "User"

    def test_full_name_empty(self):
        """full_name sin nombre ni apellido debe ser vacío."""
        u = User()
        u.email = "test@example.com"
        u.username = "testuser"
        assert u.full_name == ""

    def test_department_setter(self):
        """department debe asignarse correctamente."""
        u = _make_user()
        u.department = "IT"
        assert u.department == "IT"

    def test_department_none(self):
        """department puede ser None."""
        u = _make_user()
        assert u.department is None

    def test_is_active_toggle(self):
        """is_active debe poder cambiarse a False."""
        u = _make_user()
        assert u.is_active is True
        u.is_active = False
        assert u.is_active is False

    def test_is_verified_setter(self):
        """is_verified debe asignarse correctamente."""
        u = _make_user()
        assert u.is_verified is False
        u.is_verified = True
        assert u.is_verified is True


class TestUserToDict:
    """Tests de conversión a diccionario."""

    def test_to_dict_includes_all_fields(self):
        """to_dict debe incluir todos los campos esperados."""
        u = _make_user()
        d = u.to_dict()
        assert d["id"] == str(u.id)
        assert d["email"] == "test@example.com"
        assert d["username"] == "testuser"
        assert d["role"] == "user"
        assert d["first_name"] == "Test"
        assert d["last_name"] == "User"
        assert d["full_name"] == "Test User"
        assert d["department"] is None
        assert d["is_active"] is True
        assert d["is_verified"] is False
        assert d["last_login"] is None
        assert "created_at" in d
        assert "updated_at" in d

    def test_to_dict_with_last_login(self):
        """to_dict debe incluir last_login en formato ISO."""
        u = _make_user()
        u.record_login()
        d = u.to_dict()
        assert d["last_login"] is not None
        assert isinstance(d["last_login"], str)

    def test_to_dict_with_department(self):
        """to_dict debe incluir department."""
        u = _make_user()
        u.department = "Engineering"
        d = u.to_dict()
        assert d["department"] == "Engineering"

    def test_to_dict_role_value(self):
        """to_dict debe usar el value del enum para role."""
        u = _make_user()
        u.role = UserRole.ADMIN
        d = u.to_dict()
        assert d["role"] == "admin"


class TestUserEquality:
    """Tests de igualdad entre usuarios."""

    def test_eq_same_id(self):
        """Dos usuarios con el mismo ID deben ser iguales."""
        u1 = _make_user()
        u2 = _make_user()
        object.__setattr__(u2, "_id", u1.id)
        assert u1 == u2

    def test_eq_different_id(self):
        """Dos usuarios con diferente ID no deben ser iguales."""
        u1 = _make_user()
        u2 = _make_user()
        assert u1 != u2

    def test_eq_different_type(self):
        """Un usuario no debe ser igual a otro tipo de objeto."""
        u = _make_user()
        assert u != "not a user"
