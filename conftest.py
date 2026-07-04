"""
conftest.py — root-level pytest fixtures

Run tests:
    pytest                          
    pytest tests/identity/          
    pytest -v --tb=short            
    pytest --cov=identity --cov-report=term-missing   

Note: Tests run against local PostgreSQL on localhost:5433 (Docker port mapping)
      Not against 'db:5432' (Docker network name)
"""
import os
import pytest
from django.utils import timezone
from datetime import timedelta



os.environ.setdefault("DATABASE_URL", "postgres://learnflow:learnflow@localhost:5433/learnflow")






@pytest.fixture(autouse=True)
def celery_eager(settings):
    """All Celery tasks execute synchronously and in-process."""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True






@pytest.fixture(autouse=True)
def use_local_cache(settings):
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }






@pytest.fixture(autouse=True)
def seed_roles(db):
    from src.backend.identity.models import Role
    for name in [Role.STUDENT, Role.MENTOR, Role.STAFF, Role.ADMIN]:
        Role.objects.get_or_create(name=name, defaults={"description": name.title()})






@pytest.fixture
def make_user(db):
    """
    Factory that creates a User with all related records.
    Usage:
        user = make_user()
        admin = make_user(role="admin", is_active=True)
    """
    from src.backend.identity.models import User, UserInfo, UserSettings, Role, UserRole, StudentProfile

    def _make(
        email="user@example.com",
        password="StrongPass123!",
        first_name="Test",
        last_name="User",
        is_active=True,
        is_blocked=False,
        role="student",
    ):
        user = User.objects.create_user(
            email=email,
            password=password,
            is_active=is_active,
            is_blocked=is_blocked,
        )
        UserInfo.objects.filter(user=user).update(
            first_name=first_name,
            last_name=last_name,
        )
        if role:
            role_obj = Role.objects.get(name=role)
            UserRole.objects.create(user=user, role=role_obj)
        if role == "student":
            StudentProfile.objects.get_or_create(user=user)
        return user

    return _make


@pytest.fixture
def active_user(make_user):
    """A standard active student user."""
    return make_user(email="student@example.com", is_active=True)


@pytest.fixture
def inactive_user(make_user):
    """A user who has not verified their email."""
    return make_user(email="inactive@example.com", is_active=False)


@pytest.fixture
def blocked_user(make_user):
    return make_user(email="blocked@example.com", is_active=True, is_blocked=True)


@pytest.fixture
def admin_user(make_user):
    return make_user(email="admin@example.com", role="admin", is_active=True)






@pytest.fixture
def refresh_token(active_user):
    from src.backend.identity.models import RefreshToken
    raw, token = RefreshToken.create_for_user(
        user=active_user,
        ip_address="127.0.0.1",
        user_agent="pytest",
        device_name="Test device",
    )
    return raw, token


@pytest.fixture
def access_token(active_user):
    from src.backend.identity.tokens import JWTService
    return JWTService.create_access_token(active_user)


@pytest.fixture
def auth_headers(access_token):
    return {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}






@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authed_client(api_client, active_user, access_token):
    """APIClient pre-authenticated as active_user."""
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    from identity.tokens import JWTService
    token = JWTService.create_access_token(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client






@pytest.fixture
def verification_token(inactive_user):
    from src.backend.identity.models import EmailVerificationToken
    raw, obj = EmailVerificationToken.create_for_user(inactive_user)
    return raw, obj


@pytest.fixture
def password_reset_token(active_user):
    from src.backend.identity.models import PasswordResetToken
    raw, obj = PasswordResetToken.create_for_user(active_user)
    return raw, obj
