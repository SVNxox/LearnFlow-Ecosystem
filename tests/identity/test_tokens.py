"""
tests/identity/test_tokens.py

Unit tests for JWTService — no DB needed.
"""
from datetime import timedelta

import pytest
from django.utils import timezone


pytestmark = pytest.mark.django_db


class TestJWTService:
    def test_create_access_token_returns_string(self, active_user):
        from src.backend.identity.tokens import JWTService
        token = JWTService.create_access_token(active_user)
        assert isinstance(token, str)
        assert len(token) > 20

    def test_token_contains_correct_subject(self, active_user):
        from src.backend.identity.tokens import JWTService
        token = JWTService.create_access_token(active_user)
        payload = JWTService.decode_access_token(token)
        assert payload["sub"] == str(active_user.id)

    def test_token_contains_email(self, active_user):
        from src.backend.identity.tokens import JWTService
        token = JWTService.create_access_token(active_user)
        payload = JWTService.decode_access_token(token)
        assert payload["email"] == active_user.email

    def test_token_contains_roles(self, active_user):
        from src.backend.identity.tokens import JWTService
        token = JWTService.create_access_token(active_user)
        payload = JWTService.decode_access_token(token)
        assert "student" in payload["roles"]

    def test_token_type_is_access(self, active_user):
        from src.backend.identity.tokens import JWTService
        token = JWTService.create_access_token(active_user)
        payload = JWTService.decode_access_token(token)
        assert payload["type"] == "access"

    def test_expired_token_raises(self, active_user):
        import jwt
        from django.conf import settings
        from src.backend.identity.tokens import JWTService
        payload = {
            "sub":   str(active_user.id),
            "email": active_user.email,
            "roles": [],
            "iat":   int((timezone.now() - timedelta(hours=1)).timestamp()),
            "exp":   int((timezone.now() - timedelta(minutes=1)).timestamp()),
            "type":  "access",
        }
        expired = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        with pytest.raises(ValueError, match="Token expired"):
            JWTService.decode_access_token(expired)

    def test_tampered_token_raises(self, active_user):
        from src.backend.identity.tokens import JWTService
        token = JWTService.create_access_token(active_user)
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(ValueError):
            JWTService.decode_access_token(tampered)

    def test_garbage_token_raises(self, db):
        from src.backend.identity.tokens import JWTService
        with pytest.raises(ValueError):
            JWTService.decode_access_token("not.a.jwt")


class TestJWTAuthentication:
    def test_authenticated_request_sets_user(self, api_client, active_user, access_token):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        resp = api_client.get("/api/v1/auth/me/")
        assert resp.status_code == 200
        assert resp.data["email"] == active_user.email

    def test_missing_header_returns_401(self, api_client):
        resp = api_client.get("/api/v1/auth/me/")
        assert resp.status_code == 401

    def test_wrong_scheme_returns_401(self, api_client, access_token):
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {access_token}")
        resp = api_client.get("/api/v1/auth/me/")
        assert resp.status_code == 401

    def test_blocked_user_returns_401(self, api_client, make_user):
        from src.backend.identity.tokens import JWTService
        user = make_user(email="blk@ex.com", is_blocked=True, is_active=True)
        token = JWTService.create_access_token(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = api_client.get("/api/v1/auth/me/")
        assert resp.status_code == 401

    def test_inactive_user_returns_401(self, api_client, make_user):
        from src.backend.identity.tokens import JWTService
        user = make_user(email="inact@ex.com", is_active=False)
        token = JWTService.create_access_token(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = api_client.get("/api/v1/auth/me/")
        assert resp.status_code == 401
