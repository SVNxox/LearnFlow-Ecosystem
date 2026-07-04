"""
tests/identity/test_models.py

Unit + integration tests for identity models.
Covers: User, UserInfo, UserSettings (signals), Role, UserRole,
        RefreshToken, PasswordResetToken, EmailVerificationToken, LoginAttempt.
"""
import hashlib
import secrets
from datetime import timedelta

import pytest
from django.utils import timezone

pytestmark = pytest.mark.django_db






class TestUserModel:
    def test_create_user_normalises_email(self, db):
        from src.backend.identity.models import User
        user = User.objects.create_user(email="TEST@Example.COM", password="pass1234!")
        assert user.email == "test@example.com"

    def test_user_is_inactive_by_default(self, db):
        from src.backend.identity.models import User
        user = User.objects.create_user(email="new@ex.com", password="pass1234!")
        assert user.is_active is False

    def test_user_is_not_blocked_by_default(self, db):
        from src.backend.identity.models import User
        user = User.objects.create_user(email="u@ex.com", password="pass1234!")
        assert user.is_blocked is False

    def test_is_locked_false_when_no_lock(self, active_user):
        assert active_user.is_locked is False

    def test_is_locked_true_when_locked_until_in_future(self, active_user):
        active_user.locked_until = timezone.now() + timedelta(minutes=10)
        active_user.save()
        assert active_user.is_locked is True

    def test_is_locked_false_when_locked_until_expired(self, active_user):
        active_user.locked_until = timezone.now() - timedelta(minutes=1)
        active_user.save()
        assert active_user.is_locked is False

    def test_get_roles_returns_active_role_names(self, active_user):
        roles = active_user.get_roles()
        assert "student" in roles

    def test_has_role_true(self, active_user):
        assert active_user.has_role("student") is True

    def test_has_role_false(self, active_user):
        assert active_user.has_role("admin") is False

    def test_password_not_stored_in_plaintext(self, active_user):
        assert active_user.password != "StrongPass123!"
        assert active_user.password.startswith("bcrypt") or "$" in active_user.password

    def test_str_returns_email(self, active_user):
        assert str(active_user) == active_user.email

    def test_uuid_primary_key(self, active_user):
        import uuid
        assert isinstance(active_user.id, uuid.UUID)






class TestUserSignal:
    def test_userinfo_created_on_user_save(self, db):
        from src.backend.identity.models import User, UserInfo
        user = User.objects.create_user(email="sig@ex.com", password="pass1234!")
        assert UserInfo.objects.filter(user=user).exists()

    def test_usersettings_created_on_user_save(self, db):
        from src.backend.identity.models import User, UserSettings
        user = User.objects.create_user(email="sig2@ex.com", password="pass1234!")
        assert UserSettings.objects.filter(user=user).exists()

    def test_userinfo_defaults(self, db):
        from src.backend.identity.models import User, UserInfo
        user = User.objects.create_user(email="def@ex.com", password="pass1234!")
        info = UserInfo.objects.get(user=user)
        assert info.first_name == ""
        assert info.last_name == ""
        assert info.avatar_url is None

    def test_usersettings_defaults(self, db):
        from src.backend.identity.models import User, UserSettings
        user = User.objects.create_user(email="sett@ex.com", password="pass1234!")
        s = UserSettings.objects.get(user=user)
        assert s.language == "ru"
        assert s.timezone == "UTC"
        assert s.notify_email is True






class TestUserInfo:
    def test_save_strips_names(self, active_user):
        from src.backend.identity.models import UserInfo
        info = active_user.info
        info.first_name = "  Alisher  "
        info.last_name = "  Umarov  "
        info.save()
        info.refresh_from_db()
        assert info.first_name == "Alisher"
        assert info.last_name == "Umarov"

    def test_telegram_id_unique(self, make_user, db):
        from src.backend.identity.models import UserInfo
        from django.db import IntegrityError
        u1 = make_user(email="tg1@ex.com")
        u2 = make_user(email="tg2@ex.com")
        u1.info.telegram_id = 12345678
        u1.info.save()
        u2.info.telegram_id = 12345678
        with pytest.raises(IntegrityError):
            u2.info.save()






class TestRoleModel:
    def test_four_seed_roles_exist(self, db):
        from src.backend.identity.models import Role
        names = set(Role.objects.values_list("name", flat=True))
        assert {"student", "mentor", "staff", "admin"} <= names

    def test_duplicate_active_role_raises(self, active_user, db):
        from src.backend.identity.models import Role, UserRole
        from django.db import IntegrityError
        role = Role.objects.get(name="student")
        with pytest.raises(IntegrityError):
            UserRole.objects.create(user=active_user, role=role, is_active=True)

    def test_inactive_role_allows_duplicate(self, active_user, db):
        from src.backend.identity.models import Role, UserRole
        role = Role.objects.get(name="student")
        
        UserRole.objects.filter(user=active_user, role=role).update(is_active=False)
        
        ur = UserRole.objects.create(user=active_user, role=role, is_active=True)
        assert ur.pk is not None






class TestRefreshToken:
    def test_create_for_user_returns_raw_and_instance(self, active_user):
        from src.backend.identity.models import RefreshToken
        raw, token = RefreshToken.create_for_user(
            user=active_user, ip_address="1.2.3.4"
        )
        assert len(raw) > 20
        assert token.pk is not None

    def test_token_hash_is_sha256_of_raw(self, active_user):
        from src.backend.identity.models import RefreshToken
        raw, token = RefreshToken.create_for_user(
            user=active_user, ip_address="1.2.3.4"
        )
        expected = hashlib.sha256(raw.encode()).hexdigest()
        assert token.token_hash == expected

    def test_raw_token_not_stored(self, active_user):
        from src.backend.identity.models import RefreshToken
        raw, token = RefreshToken.create_for_user(
            user=active_user, ip_address="1.2.3.4"
        )
        assert token.token_hash != raw

    def test_get_by_raw_finds_token(self, active_user):
        from src.backend.identity.models import RefreshToken
        raw, token = RefreshToken.create_for_user(
            user=active_user, ip_address="1.2.3.4"
        )
        found = RefreshToken.get_by_raw(raw)
        assert found.pk == token.pk

    def test_get_by_raw_returns_none_for_garbage(self, db):
        from src.backend.identity.models import RefreshToken
        assert RefreshToken.get_by_raw("garbage-token-xyz") is None

    def test_is_active_true_for_fresh_token(self, active_user):
        from src.backend.identity.models import RefreshToken
        _, token = RefreshToken.create_for_user(user=active_user, ip_address="1.2.3.4")
        assert token.is_active is True

    def test_is_active_false_after_revoke(self, active_user):
        from src.backend.identity.models import RefreshToken
        _, token = RefreshToken.create_for_user(user=active_user, ip_address="1.2.3.4")
        token.revoke()
        assert token.is_active is False

    def test_is_active_false_when_expired(self, active_user):
        from src.backend.identity.models import RefreshToken
        _, token = RefreshToken.create_for_user(user=active_user, ip_address="1.2.3.4")
        token.expires_at = timezone.now() - timedelta(seconds=1)
        token.save()
        assert token.is_active is False

    def test_expires_at_set_to_30_days(self, active_user):
        from src.backend.identity.models import RefreshToken
        before = timezone.now()
        _, token = RefreshToken.create_for_user(user=active_user, ip_address="1.2.3.4")
        after = timezone.now()
        expected_low  = before + timedelta(days=29, hours=23)
        expected_high = after  + timedelta(days=30, seconds=5)
        assert expected_low < token.expires_at < expected_high






class TestEmailVerificationToken:
    def test_create_invalidates_previous_tokens(self, inactive_user):
        from src.backend.identity.models import EmailVerificationToken
        _, t1 = EmailVerificationToken.create_for_user(inactive_user)
        _, t2 = EmailVerificationToken.create_for_user(inactive_user)
        t1.refresh_from_db()
        assert t1.verified_at is not None  
        assert t2.verified_at is None      

    def test_is_valid_true_for_fresh(self, inactive_user):
        from src.backend.identity.models import EmailVerificationToken
        _, token = EmailVerificationToken.create_for_user(inactive_user)
        assert token.is_valid is True

    def test_is_valid_false_after_expiry(self, inactive_user):
        from src.backend.identity.models import EmailVerificationToken
        _, token = EmailVerificationToken.create_for_user(inactive_user)
        token.expires_at = timezone.now() - timedelta(hours=1)
        token.save()
        assert token.is_valid is False

    def test_get_by_raw_correct(self, inactive_user):
        from src.backend.identity.models import EmailVerificationToken
        raw, token = EmailVerificationToken.create_for_user(inactive_user)
        found = EmailVerificationToken.get_by_raw(raw)
        assert found.pk == token.pk

    def test_get_by_raw_wrong_token(self, db):
        from src.backend.identity.models import EmailVerificationToken
        assert EmailVerificationToken.get_by_raw("wrong") is None






class TestPasswordResetToken:
    def test_create_expires_previous_tokens(self, active_user):
        from src.backend.identity.models import PasswordResetToken
        _, t1 = PasswordResetToken.create_for_user(active_user)
        _, t2 = PasswordResetToken.create_for_user(active_user)
        t1.refresh_from_db()
        assert t1.used_at is not None

    def test_is_valid_true_for_fresh(self, active_user):
        from src.backend.identity.models import PasswordResetToken
        _, token = PasswordResetToken.create_for_user(active_user)
        assert token.is_valid is True

    def test_is_valid_false_after_expiry(self, active_user):
        from src.backend.identity.models import PasswordResetToken
        _, token = PasswordResetToken.create_for_user(active_user)
        token.expires_at = timezone.now() - timedelta(minutes=1)
        token.save()
        assert token.is_valid is False

    def test_is_valid_false_after_use(self, active_user):
        from src.backend.identity.models import PasswordResetToken
        _, token = PasswordResetToken.create_for_user(active_user)
        token.used_at = timezone.now()
        token.save()
        assert token.is_valid is False
