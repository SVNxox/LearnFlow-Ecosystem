"""
tests/identity/test_services.py

Integration tests for identity/services.py.
All email tasks are mocked — no SMTP needed.
Tests cover: register, login, refresh, logout, verify, reset password, change password.
"""
from datetime import timedelta
from unittest.mock import patch, MagicMock

import pytest
from django.utils import timezone

pytestmark = pytest.mark.django_db






def _fake_request(ip="127.0.0.1", ua="pytest/1.0"):
    """Minimal mock of HttpRequest for service functions."""
    req = MagicMock()
    req.META = {"REMOTE_ADDR": ip, "HTTP_USER_AGENT": ua}
    return req






class TestRegisterUser:
    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_creates_user_record(self, mock_task):
        from src.backend.identity.services import register_user
        from src.backend.identity.models import User
        user = register_user("New@Example.com", "StrongPass1!", "Ali", "Umarov")
        assert User.objects.filter(email="new@example.com").exists()

    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_user_starts_inactive(self, mock_task):
        from src.backend.identity.services import register_user
        user = register_user("inactive@ex.com", "StrongPass1!", "Ali", "U")
        assert user.is_active is False

    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_email_normalised_to_lowercase(self, mock_task):
        from src.backend.identity.services import register_user
        user = register_user("UPPER@EX.COM", "StrongPass1!", "Ali", "U")
        assert user.email == "upper@ex.com"

    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_student_role_assigned(self, mock_task):
        from src.backend.identity.services import register_user
        user = register_user("role@ex.com", "StrongPass1!", "Ali", "U")
        assert user.has_role("student")

    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_student_profile_created(self, mock_task):
        from src.backend.identity.services import register_user
        from src.backend.identity.models import StudentProfile
        user = register_user("sp@ex.com", "StrongPass1!", "Ali", "U")
        assert StudentProfile.objects.filter(user=user).exists()

    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_userinfo_names_saved(self, mock_task):
        from src.backend.identity.services import register_user
        user = register_user("name@ex.com", "StrongPass1!", "Bobur", "Karimov")
        user.info.refresh_from_db()
        assert user.info.first_name == "Bobur"
        assert user.info.last_name == "Karimov"

    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_verification_email_queued(self, mock_task):
        from src.backend.identity.services import register_user
        register_user("email@ex.com", "StrongPass1!", "A", "B")
        mock_task.assert_called_once()

    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_duplicate_email_raises_auth_error(self, mock_task, active_user):
        from src.backend.identity.services import register_user, AuthError
        with pytest.raises(AuthError) as exc_info:
            register_user(active_user.email, "StrongPass1!", "A", "B")
        assert exc_info.value.code == "register_failed"

    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_register_is_atomic_on_role_missing(self, mock_task):
        from src.backend.identity.services import register_user
        from src.backend.identity.models import Role, User
        Role.objects.filter(name="student").delete()
        with pytest.raises(Exception):
            register_user("atom@ex.com", "StrongPass1!", "A", "B")
        assert not User.objects.filter(email="atom@ex.com").exists()






class TestLoginUser:
    def test_successful_login_returns_tokens(self, active_user):
        from src.backend.identity.services import login_user
        result = login_user(active_user.email, "StrongPass123!", _fake_request())
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "Bearer"

    def test_successful_login_returns_user(self, active_user):
        from src.backend.identity.services import login_user
        result = login_user(active_user.email, "StrongPass123!", _fake_request())
        assert result["user"].pk == active_user.pk

    def test_wrong_password_raises(self, active_user):
        from src.backend.identity.services import login_user, AuthError
        with pytest.raises(AuthError) as exc_info:
            login_user(active_user.email, "WRONG", _fake_request())
        assert exc_info.value.code == "invalid_credentials"

    def test_nonexistent_email_raises_same_error(self, db):
        from src.backend.identity.services import login_user, AuthError
        with pytest.raises(AuthError) as exc_info:
            login_user("ghost@ex.com", "WRONG", _fake_request())
        assert exc_info.value.code == "invalid_credentials"

    def test_inactive_user_cannot_login(self, inactive_user):
        from src.backend.identity.services import login_user, AuthError
        with pytest.raises(AuthError) as exc_info:
            login_user(inactive_user.email, "StrongPass123!", _fake_request())
        assert exc_info.value.code == "email_not_verified"

    def test_blocked_user_cannot_login(self, blocked_user):
        from src.backend.identity.services import login_user, AuthError
        with pytest.raises(AuthError) as exc_info:
            login_user(blocked_user.email, "StrongPass123!", _fake_request())
        assert exc_info.value.code == "account_blocked"

    def test_locked_user_cannot_login(self, active_user):
        from src.backend.identity.services import login_user, AuthError
        active_user.locked_until = timezone.now() + timedelta(minutes=10)
        active_user.save()
        with pytest.raises(AuthError) as exc_info:
            login_user(active_user.email, "StrongPass123!", _fake_request())
        assert exc_info.value.code == "account_locked"

    def test_failed_login_records_attempt(self, active_user):
        from src.backend.identity.services import login_user, AuthError
        from src.backend.identity.models import LoginAttempt
        before = LoginAttempt.objects.count()
        with pytest.raises(AuthError):
            login_user(active_user.email, "BAD", _fake_request())
        assert LoginAttempt.objects.count() == before + 1
        attempt = LoginAttempt.objects.last()
        assert attempt.success is False

    def test_successful_login_records_attempt(self, active_user):
        from src.backend.identity.services import login_user
        from src.backend.identity.models import LoginAttempt
        login_user(active_user.email, "StrongPass123!", _fake_request())
        attempt = LoginAttempt.objects.last()
        assert attempt.success is True

    def test_successful_login_resets_failed_attempts(self, active_user):
        active_user.failed_login_attempts = 3
        active_user.save()
        from src.backend.identity.services import login_user
        login_user(active_user.email, "StrongPass123!", _fake_request())
        active_user.refresh_from_db()
        assert active_user.failed_login_attempts == 0

    def test_failed_login_increments_failed_attempts(self, active_user):
        from src.backend.identity.services import login_user, AuthError
        with pytest.raises(AuthError):
            login_user(active_user.email, "BAD", _fake_request())
        active_user.refresh_from_db()
        assert active_user.failed_login_attempts == 1

    def test_lockout_after_max_attempts(self, active_user):
        from src.backend.identity.services import login_user, AuthError, MAX_FAILED_ATTEMPTS
        for _ in range(MAX_FAILED_ATTEMPTS):
            with pytest.raises(AuthError):
                login_user(active_user.email, "BAD", _fake_request())
        active_user.refresh_from_db()
        assert active_user.locked_until is not None
        assert active_user.locked_until > timezone.now()

    def test_ip_rate_limit_raises_after_20_failures(self, db, active_user):
        from django.core.cache import cache
        from src.backend.identity.services import login_user, AuthError
        cache.set("auth:fails:127.0.0.1", 20, timeout=900)
        with pytest.raises(AuthError) as exc_info:
            login_user("any@ex.com", "ANY", _fake_request(ip="127.0.0.1"))
        assert exc_info.value.code == "ip_rate_limit"

    def test_login_updates_last_login_at(self, active_user):
        from src.backend.identity.services import login_user
        login_user(active_user.email, "StrongPass123!", _fake_request())
        active_user.refresh_from_db()
        assert active_user.last_login_at is not None

    def test_login_updates_last_login_ip(self, active_user):
        from src.backend.identity.services import login_user
        login_user(active_user.email, "StrongPass123!", _fake_request(ip="10.0.0.1"))
        active_user.refresh_from_db()
        assert active_user.last_login_ip == "10.0.0.1"

    def test_login_creates_refresh_token(self, active_user):
        from src.backend.identity.services import login_user
        from src.backend.identity.models import RefreshToken
        before = RefreshToken.objects.filter(user=active_user).count()
        login_user(active_user.email, "StrongPass123!", _fake_request())
        assert RefreshToken.objects.filter(user=active_user).count() == before + 1

    def test_login_xff_header_used_as_ip(self, active_user):
        from src.backend.identity.services import login_user, _get_client_ip
        req = MagicMock()
        req.META = {
            "HTTP_X_FORWARDED_FOR": "203.0.113.5, 10.0.0.1",
            "REMOTE_ADDR": "10.0.0.1",
        }
        ip = _get_client_ip(req)
        assert ip == "203.0.113.5"






class TestRefreshAccessToken:
    def test_returns_new_tokens(self, active_user, refresh_token):
        from src.backend.identity.services import refresh_access_token
        raw, _ = refresh_token
        result = refresh_access_token(raw, _fake_request())
        assert "access_token" in result
        assert "refresh_token" in result

    def test_old_token_is_revoked(self, active_user, refresh_token):
        from src.backend.identity.services import refresh_access_token
        from src.backend.identity.models import RefreshToken
        raw, old_token = refresh_token
        refresh_access_token(raw, _fake_request())
        old_token.refresh_from_db()
        assert old_token.revoked_at is not None

    def test_new_refresh_token_is_different(self, active_user, refresh_token):
        from src.backend.identity.services import refresh_access_token
        raw, _ = refresh_token
        result = refresh_access_token(raw, _fake_request())
        assert result["refresh_token"] != raw

    def test_invalid_token_raises(self, db):
        from src.backend.identity.services import refresh_access_token, AuthError
        with pytest.raises(AuthError) as exc_info:
            refresh_access_token("bogus-token", _fake_request())
        assert exc_info.value.code == "invalid_token"

    def test_revoked_token_raises_and_nukes_all_sessions(self, active_user, refresh_token):
        from src.backend.identity.services import refresh_access_token, AuthError
        from src.backend.identity.models import RefreshToken
        raw, token = refresh_token
        token.revoke()
        
        RefreshToken.create_for_user(user=active_user, ip_address="9.9.9.9")
        with pytest.raises(AuthError) as exc_info:
            refresh_access_token(raw, _fake_request())
        assert exc_info.value.code == "token_reuse"
        
        active_count = RefreshToken.objects.filter(
            user=active_user, revoked_at__isnull=True
        ).count()
        assert active_count == 0

    def test_expired_token_raises(self, active_user, refresh_token):
        from src.backend.identity.services import refresh_access_token, AuthError
        raw, token = refresh_token
        token.expires_at = timezone.now() - timedelta(days=1)
        token.save()
        with pytest.raises(AuthError) as exc_info:
            refresh_access_token(raw, _fake_request())
        assert exc_info.value.code == "token_expired"

    def test_blocked_user_cannot_refresh(self, active_user, refresh_token):
        from src.backend.identity.services import refresh_access_token, AuthError
        raw, _ = refresh_token
        active_user.is_blocked = True
        active_user.save()
        with pytest.raises(AuthError) as exc_info:
            refresh_access_token(raw, _fake_request())
        assert exc_info.value.code == "account_unavailable"






class TestLogout:
    def test_logout_revokes_token(self, active_user, refresh_token):
        from src.backend.identity.services import logout_user
        from src.backend.identity.models import RefreshToken
        raw, token = refresh_token
        logout_user(raw)
        token.refresh_from_db()
        assert token.revoked_at is not None

    def test_logout_invalid_token_does_nothing(self, db):
        from src.backend.identity.services import logout_user
        
        logout_user("nonexistent-token-xyz")

    def test_logout_all_revokes_all_sessions(self, active_user):
        from src.backend.identity.services import logout_all_sessions
        from src.backend.identity.models import RefreshToken
        RefreshToken.create_for_user(active_user, "1.1.1.1")
        RefreshToken.create_for_user(active_user, "2.2.2.2")
        count = logout_all_sessions(active_user)
        assert count == 2
        assert RefreshToken.objects.filter(
            user=active_user, revoked_at__isnull=True
        ).count() == 0

    def test_logout_all_returns_revoked_count(self, active_user):
        from src.backend.identity.services import logout_all_sessions
        from src.backend.identity.models import RefreshToken
        RefreshToken.create_for_user(active_user, "1.1.1.1")
        RefreshToken.create_for_user(active_user, "2.2.2.2")
        count = logout_all_sessions(active_user)
        assert count == 2






class TestVerifyEmail:
    def test_valid_token_activates_user(self, inactive_user, verification_token):
        from src.backend.identity.services import verify_email
        raw, _ = verification_token
        verify_email(raw)
        inactive_user.refresh_from_db()
        assert inactive_user.is_active is True

    def test_valid_token_marks_verified_at(self, inactive_user, verification_token):
        from src.backend.identity.services import verify_email
        from src.backend.identity.models import EmailVerificationToken
        raw, token = verification_token
        verify_email(raw)
        token.refresh_from_db()
        assert token.verified_at is not None

    def test_invalid_token_raises(self, db):
        from src.backend.identity.services import verify_email, AuthError
        with pytest.raises(AuthError) as exc_info:
            verify_email("invalid-token")
        assert exc_info.value.code == "invalid_token"

    def test_expired_token_raises(self, inactive_user, verification_token):
        from src.backend.identity.services import verify_email, AuthError
        raw, token = verification_token
        token.expires_at = timezone.now() - timedelta(hours=1)
        token.save()
        with pytest.raises(AuthError) as exc_info:
            verify_email(raw)
        assert exc_info.value.code == "invalid_token"

    def test_already_active_user_raises(self, active_user):
        from src.backend.identity.services import verify_email, AuthError
        from src.backend.identity.models import EmailVerificationToken
        raw, _ = EmailVerificationToken.create_for_user(active_user)
        
        with pytest.raises(AuthError) as exc_info:
            verify_email(raw)
        assert exc_info.value.code == "already_verified"

    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_resend_rate_limited(self, mock_task, inactive_user):
        from src.backend.identity.services import resend_verification_email, AuthError
        resend_verification_email(inactive_user.email)
        with pytest.raises(AuthError) as exc_info:
            resend_verification_email(inactive_user.email)
        assert exc_info.value.code == "rate_limited"

    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_resend_unknown_email_silent(self, mock_task, db):
        from src.backend.identity.services import resend_verification_email
        
        resend_verification_email("ghost@ex.com")
        mock_task.assert_not_called()

    @patch("src.backend.identity.tasks.send_verification_email.delay")
    def test_resend_already_active_silent(self, mock_task, active_user):
        from src.backend.identity.services import resend_verification_email
        resend_verification_email(active_user.email)
        mock_task.assert_not_called()






class TestPasswordReset:
    @patch("src.backend.identity.tasks.send_password_reset_email.delay")
    def test_request_queues_task_for_active_user(self, mock_task, active_user):
        from src.backend.identity.services import request_password_reset
        request_password_reset(active_user.email)
        mock_task.assert_called_once()

    @patch("src.backend.identity.tasks.send_password_reset_email.delay")
    def test_request_silent_for_unknown_email(self, mock_task, db):
        from src.backend.identity.services import request_password_reset
        request_password_reset("ghost@ex.com")
        mock_task.assert_not_called()

    @patch("src.backend.identity.tasks.send_password_reset_email.delay")
    def test_request_silent_for_inactive_user(self, mock_task, inactive_user):
        from src.backend.identity.services import request_password_reset
        request_password_reset(inactive_user.email)
        mock_task.assert_not_called()

    def test_reset_with_valid_token_changes_password(self, active_user, password_reset_token):
        from src.backend.identity.services import reset_password
        from django.contrib.auth.hashers import check_password
        raw, _ = password_reset_token
        reset_password(raw, "NewSecurePass99!")
        active_user.refresh_from_db()
        assert check_password("NewSecurePass99!", active_user.password)

    def test_reset_marks_token_as_used(self, active_user, password_reset_token):
        from src.backend.identity.services import reset_password
        from src.backend.identity.models import PasswordResetToken
        raw, token = password_reset_token
        reset_password(raw, "NewSecurePass99!")
        token.refresh_from_db()
        assert token.used_at is not None

    def test_reset_revokes_all_sessions(self, active_user, password_reset_token, refresh_token):
        from src.backend.identity.services import reset_password
        from src.backend.identity.models import RefreshToken
        raw_reset, _ = password_reset_token
        reset_password(raw_reset, "NewSecurePass99!")
        active_count = RefreshToken.objects.filter(
            user=active_user, revoked_at__isnull=True
        ).count()
        assert active_count == 0

    def test_reset_invalid_token_raises(self, db):
        from src.backend.identity.services import reset_password, AuthError
        with pytest.raises(AuthError) as exc_info:
            reset_password("bad-token", "NewSecurePass99!")
        assert exc_info.value.code == "invalid_token"

    def test_reset_expired_token_raises(self, active_user, password_reset_token):
        from src.backend.identity.services import reset_password, AuthError
        raw, token = password_reset_token
        token.expires_at = timezone.now() - timedelta(minutes=1)
        token.save()
        with pytest.raises(AuthError) as exc_info:
            reset_password(raw, "NewSecurePass99!")
        assert exc_info.value.code == "invalid_token"

    def test_reset_used_token_raises(self, active_user, password_reset_token):
        from src.backend.identity.services import reset_password, AuthError
        raw, token = password_reset_token
        token.used_at = timezone.now()
        token.save()
        with pytest.raises(AuthError) as exc_info:
            reset_password(raw, "NewSecurePass99!")
        assert exc_info.value.code == "invalid_token"






class TestChangePassword:
    def test_change_succeeds_with_correct_old_password(self, active_user):
        from src.backend.identity.services import change_password
        from django.contrib.auth.hashers import check_password
        change_password(active_user, "StrongPass123!", "NewPass456!")
        active_user.refresh_from_db()
        assert check_password("NewPass456!", active_user.password)

    def test_change_wrong_old_password_raises(self, active_user):
        from src.backend.identity.services import change_password, AuthError
        with pytest.raises(AuthError) as exc_info:
            change_password(active_user, "WRONG", "NewPass456!")
        assert exc_info.value.code == "wrong_password"

    def test_change_revokes_all_sessions(self, active_user, refresh_token):
        from src.backend.identity.services import change_password
        from src.backend.identity.models import RefreshToken
        change_password(active_user, "StrongPass123!", "NewPass456!")
        active_count = RefreshToken.objects.filter(
            user=active_user, revoked_at__isnull=True
        ).count()
        assert active_count == 0
