"""
tests/identity/test_api.py

Full HTTP stack tests via DRF APIClient.
Every endpoint is covered: register, login, refresh, logout, verify,
resend, password reset, me, settings, sessions.
"""
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

pytestmark = pytest.mark.django_db






REGISTER_URL      = "/api/v1/auth/register/"
LOGIN_URL         = "/api/v1/auth/login/"
REFRESH_URL       = "/api/v1/auth/token/refresh/"
LOGOUT_URL        = "/api/v1/auth/logout/"
LOGOUT_ALL_URL    = "/api/v1/auth/logout/all/"
VERIFY_URL        = "/api/v1/auth/verify-email/"
RESEND_URL        = "/api/v1/auth/verify-email/resend/"
RESET_URL         = "/api/v1/auth/password-reset/"
RESET_CONFIRM_URL = "/api/v1/auth/password-reset/confirm/"
ME_URL            = "/api/v1/auth/me/"
ME_PASSWORD_URL   = "/api/v1/auth/me/password/"
ME_SETTINGS_URL   = "/api/v1/auth/me/settings/"
SESSIONS_URL      = "/api/v1/auth/me/sessions/"






class TestRegisterAPI:
    PAYLOAD = {
        "email": "newuser@ex.com",
        "password": "StrongPass1!",
        "first_name": "New",
        "last_name": "User",
    }

    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_201_on_success(self, mock_task, api_client):
        resp = api_client.post(REGISTER_URL, self.PAYLOAD, format="json")
        assert resp.status_code == status.HTTP_201_CREATED

    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_response_contains_detail(self, mock_task, api_client):
        resp = api_client.post(REGISTER_URL, self.PAYLOAD, format="json")
        assert "detail" in resp.data

    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_duplicate_email_returns_400(self, mock_task, api_client, active_user):
        payload = {**self.PAYLOAD, "email": active_user.email}
        resp = api_client.post(REGISTER_URL, payload, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_field_returns_400(self, api_client):
        resp = api_client.post(REGISTER_URL, {"email": "x@ex.com"}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_email_returns_400(self, api_client):
        payload = {**self.PAYLOAD, "email": "not-an-email"}
        resp = api_client.post(REGISTER_URL, payload, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_short_password_returns_400(self, api_client):
        payload = {**self.PAYLOAD, "email": "short@ex.com", "password": "123"}
        resp = api_client.post(REGISTER_URL, payload, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST






class TestLoginAPI:
    def test_200_on_valid_credentials(self, api_client, active_user):
        resp = api_client.post(
            LOGIN_URL,
            {"email": active_user.email, "password": "StrongPass123!"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK

    def test_response_contains_tokens(self, api_client, active_user):
        resp = api_client.post(
            LOGIN_URL,
            {"email": active_user.email, "password": "StrongPass123!"},
            format="json",
        )
        assert "access_token" in resp.data
        assert "refresh_token" in resp.data
        assert resp.data["token_type"] == "Bearer"

    def test_401_on_wrong_password(self, api_client, active_user):
        resp = api_client.post(
            LOGIN_URL,
            {"email": active_user.email, "password": "WRONG"},
            format="json",
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_401_on_inactive_user(self, api_client, inactive_user):
        resp = api_client.post(
            LOGIN_URL,
            {"email": inactive_user.email, "password": "StrongPass123!"},
            format="json",
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.data["code"] == "email_not_verified"

    def test_401_on_blocked_user(self, api_client, blocked_user):
        resp = api_client.post(
            LOGIN_URL,
            {"email": blocked_user.email, "password": "StrongPass123!"},
            format="json",
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.data["code"] == "account_blocked"

    def test_400_on_missing_fields(self, api_client):
        resp = api_client.post(LOGIN_URL, {"email": "x@x.com"}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_error_response_format(self, api_client, active_user):
        resp = api_client.post(
            LOGIN_URL,
            {"email": active_user.email, "password": "WRONG"},
            format="json",
        )
        assert "error" in resp.data
        assert "code" in resp.data






class TestTokenRefreshAPI:
    def test_200_on_valid_refresh_token(self, api_client, refresh_token):
        raw, _ = refresh_token
        resp = api_client.post(REFRESH_URL, {"refresh_token": raw}, format="json")
        assert resp.status_code == status.HTTP_200_OK

    def test_returns_new_access_and_refresh(self, api_client, refresh_token):
        raw, _ = refresh_token
        resp = api_client.post(REFRESH_URL, {"refresh_token": raw}, format="json")
        assert "access_token" in resp.data
        assert "refresh_token" in resp.data

    def test_401_on_invalid_token(self, api_client):
        resp = api_client.post(REFRESH_URL, {"refresh_token": "garbage"}, format="json")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_old_token_invalid_after_refresh(self, api_client, refresh_token):
        raw, _ = refresh_token
        api_client.post(REFRESH_URL, {"refresh_token": raw}, format="json")
        
        resp2 = api_client.post(REFRESH_URL, {"refresh_token": raw}, format="json")
        assert resp2.status_code == status.HTTP_401_UNAUTHORIZED






class TestLogoutAPI:
    def test_204_on_valid_refresh_token(self, authed_client, refresh_token):
        raw, _ = refresh_token
        resp = authed_client.post(LOGOUT_URL, {"refresh_token": raw}, format="json")
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_401_without_auth(self, api_client, refresh_token):
        raw, _ = refresh_token
        resp = api_client.post(LOGOUT_URL, {"refresh_token": raw}, format="json")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_all_204(self, authed_client):
        resp = authed_client.post(LOGOUT_ALL_URL)
        assert resp.status_code == status.HTTP_200_OK
        assert "revoked" in resp.data






class TestEmailVerifyAPI:
    def test_200_on_valid_token(self, api_client, inactive_user, verification_token):
        raw, _ = verification_token
        resp = api_client.get(VERIFY_URL, {"token": raw})
        assert resp.status_code == status.HTTP_200_OK

    def test_user_becomes_active(self, api_client, inactive_user, verification_token):
        raw, _ = verification_token
        api_client.get(VERIFY_URL, {"token": raw})
        inactive_user.refresh_from_db()
        assert inactive_user.is_active is True

    def test_400_on_invalid_token(self, api_client):
        resp = api_client.get(VERIFY_URL, {"token": "bad-token"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_400_on_expired_token(self, api_client, inactive_user, verification_token):
        raw, token = verification_token
        token.expires_at = timezone.now() - timedelta(hours=1)
        token.save()
        resp = api_client.get(VERIFY_URL, {"token": raw})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST






class TestEmailResendAPI:
    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_200_always(self, mock_task, api_client, inactive_user):
        resp = api_client.post(RESEND_URL, {"email": inactive_user.email}, format="json")
        assert resp.status_code == status.HTTP_200_OK

    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_200_for_unknown_email(self, mock_task, api_client):
        
        resp = api_client.post(RESEND_URL, {"email": "ghost@ex.com"}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        mock_task.assert_not_called()

    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_429_on_rate_limit(self, mock_task, api_client, inactive_user):
        api_client.post(RESEND_URL, {"email": inactive_user.email}, format="json")
        resp = api_client.post(RESEND_URL, {"email": inactive_user.email}, format="json")
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS






class TestPasswordResetAPI:
    @patch("src.backend.identity.tasks.send_password_reset_email.delay")
    def test_200_always(self, mock_task, api_client, active_user):
        resp = api_client.post(RESET_URL, {"email": active_user.email}, format="json")
        assert resp.status_code == status.HTTP_200_OK

    @patch("src.backend.identity.tasks.send_password_reset_email.delay")
    def test_200_for_unknown_email(self, mock_task, api_client):
        resp = api_client.post(RESET_URL, {"email": "ghost@ex.com"}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        mock_task.assert_not_called()

    def test_400_on_missing_email(self, api_client):
        resp = api_client.post(RESET_URL, {}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST






class TestPasswordResetConfirmAPI:
    def test_200_on_valid_reset(self, api_client, active_user, password_reset_token):
        raw, _ = password_reset_token
        resp = api_client.post(
            RESET_CONFIRM_URL,
            {"token": raw, "new_password": "FreshPass99!"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK

    def test_password_actually_changed(self, api_client, active_user, password_reset_token):
        from django.contrib.auth.hashers import check_password
        raw, _ = password_reset_token
        api_client.post(
            RESET_CONFIRM_URL,
            {"token": raw, "new_password": "FreshPass99!"},
            format="json",
        )
        active_user.refresh_from_db()
        assert check_password("FreshPass99!", active_user.password)

    def test_400_on_bad_token(self, api_client):
        resp = api_client.post(
            RESET_CONFIRM_URL,
            {"token": "garbage", "new_password": "FreshPass99!"},
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_400_on_weak_password(self, api_client, active_user, password_reset_token):
        raw, _ = password_reset_token
        resp = api_client.post(
            RESET_CONFIRM_URL,
            {"token": raw, "new_password": "123"},
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST






class TestMeAPI:
    def test_get_returns_profile(self, authed_client, active_user):
        resp = authed_client.get(ME_URL)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["email"] == active_user.email

    def test_get_includes_info_and_settings(self, authed_client):
        resp = authed_client.get(ME_URL)
        assert "info" in resp.data
        assert "settings" in resp.data
        assert "roles" in resp.data

    def test_get_does_not_expose_password(self, authed_client):
        resp = authed_client.get(ME_URL)
        assert "password" not in resp.data
        assert "password_hash" not in resp.data

    def test_get_does_not_expose_last_login_ip(self, authed_client):
        resp = authed_client.get(ME_URL)
        assert "last_login_ip" not in resp.data

    def test_401_without_auth(self, api_client):
        resp = api_client.get(ME_URL)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patch_updates_name(self, authed_client, active_user):
        resp = authed_client.patch(
            ME_URL,
            {"first_name": "Updated", "last_name": "Name"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        active_user.info.refresh_from_db()
        assert active_user.info.first_name == "Updated"

    def test_patch_partial_update(self, authed_client, active_user):
        resp = authed_client.patch(ME_URL, {"bio": "Hello!"}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        active_user.info.refresh_from_db()
        assert active_user.info.bio == "Hello!"

    def test_expired_token_returns_401(self, api_client, active_user):
        import jwt
        from django.conf import settings
        from django.utils import timezone
        payload = {
            "sub":   str(active_user.id),
            "email": active_user.email,
            "roles": [],
            "iat":   int((timezone.now() - timedelta(hours=1)).timestamp()),
            "exp":   int((timezone.now() - timedelta(minutes=1)).timestamp()),
            "type":  "access",
        }
        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {expired_token}")
        resp = api_client.get(ME_URL)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED






class TestChangePasswordAPI:
    def test_200_on_correct_password(self, authed_client):
        resp = authed_client.post(
            ME_PASSWORD_URL,
            {"old_password": "StrongPass123!", "new_password": "NewPass456!"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK

    def test_400_on_wrong_old_password(self, authed_client):
        resp = authed_client.post(
            ME_PASSWORD_URL,
            {"old_password": "WRONG", "new_password": "NewPass456!"},
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_401_without_auth(self, api_client):
        resp = api_client.post(ME_PASSWORD_URL, {}, format="json")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED






class TestUserSettingsAPI:
    def test_get_settings(self, authed_client):
        resp = authed_client.get(ME_SETTINGS_URL)
        assert resp.status_code == status.HTTP_200_OK
        assert "language" in resp.data
        assert "timezone" in resp.data

    def test_patch_settings(self, authed_client, active_user):
        resp = authed_client.patch(
            ME_SETTINGS_URL,
            {"language": "en", "notify_telegram": False},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        active_user.settings.refresh_from_db()
        assert active_user.settings.language == "en"
        assert active_user.settings.notify_telegram is False

    def test_401_without_auth(self, api_client):
        resp = api_client.get(ME_SETTINGS_URL)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED






class TestSessionsAPI:
    def test_get_lists_active_sessions(self, authed_client, refresh_token):
        resp = authed_client.get(SESSIONS_URL)
        assert resp.status_code == status.HTTP_200_OK
        assert isinstance(resp.data, list)
        assert len(resp.data) >= 1

    def test_revoked_sessions_not_listed(self, authed_client, active_user, refresh_token):
        raw, token = refresh_token
        token.revoke()
        resp = authed_client.get(SESSIONS_URL)
        session_ids = [s["id"] for s in resp.data]
        assert str(token.id) not in session_ids

    def test_delete_revokes_session(self, authed_client, active_user, refresh_token):
        raw, token = refresh_token
        resp = authed_client.delete(f"{SESSIONS_URL}{token.id}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        token.refresh_from_db()
        assert token.revoked_at is not None

    def test_delete_another_users_session_returns_404(self, authed_client, make_user):
        from src.backend.identity.models import RefreshToken
        other = make_user(email="other@ex.com")
        _, other_token = RefreshToken.create_for_user(other, "5.5.5.5")
        resp = authed_client.delete(f"{SESSIONS_URL}{other_token.id}/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_401_without_auth(self, api_client):
        resp = api_client.get(SESSIONS_URL)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
