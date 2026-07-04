"""
tests/identity/test_permissions.py

Unit tests for custom DRF permission classes.
"""
from unittest.mock import MagicMock
import pytest

pytestmark = pytest.mark.django_db


def _make_request(user):
    req = MagicMock()
    req.user = user
    req.user.is_authenticated = True
    return req


class TestIsAdmin:
    def test_admin_user_allowed(self, admin_user):
        from src.backend.identity.permissions import IsAdmin
        perm = IsAdmin()
        req = _make_request(admin_user)
        assert perm.has_permission(req, None) is True

    def test_student_user_denied(self, active_user):
        from src.backend.identity.permissions import IsAdmin
        perm = IsAdmin()
        req = _make_request(active_user)
        assert perm.has_permission(req, None) is False

    def test_unauthenticated_denied(self):
        from src.backend.identity.permissions import IsAdmin
        perm = IsAdmin()
        req = MagicMock()
        req.user = None
        assert perm.has_permission(req, None) is False


class TestIsMentor:
    def test_mentor_allowed(self, make_user):
        from src.backend.identity.permissions import IsMentor
        mentor = make_user(email="m@ex.com", role="mentor")
        req = _make_request(mentor)
        assert IsMentor().has_permission(req, None) is True

    def test_admin_allowed(self, admin_user):
        from src.backend.identity.permissions import IsMentor
        req = _make_request(admin_user)
        assert IsMentor().has_permission(req, None) is True

    def test_student_denied(self, active_user):
        from src.backend.identity.permissions import IsMentor
        req = _make_request(active_user)
        assert IsMentor().has_permission(req, None) is False


class TestIsOwnerOrAdmin:
    def test_owner_has_object_permission(self, active_user):
        from src.backend.identity.permissions import IsOwnerOrAdmin
        perm = IsOwnerOrAdmin()
        req = _make_request(active_user)
        obj = MagicMock()
        obj.user_id = active_user.id
        assert perm.has_object_permission(req, None, obj) is True

    def test_non_owner_denied(self, active_user, make_user):
        from src.backend.identity.permissions import IsOwnerOrAdmin
        other = make_user(email="other@ex.com")
        perm = IsOwnerOrAdmin()
        req = _make_request(active_user)
        obj = MagicMock()
        obj.user_id = other.id
        assert perm.has_object_permission(req, None, obj) is False

    def test_admin_can_access_any_object(self, admin_user, active_user):
        from src.backend.identity.permissions import IsOwnerOrAdmin
        perm = IsOwnerOrAdmin()
        req = _make_request(admin_user)
        obj = MagicMock()
        obj.user_id = active_user.id
        assert perm.has_object_permission(req, None, obj) is True
