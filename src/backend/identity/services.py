import logging
import re
from datetime import timedelta

from django.contrib.auth import password_validation
from user_agents import parse

from django.contrib.auth.hashers import check_password, make_password
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from src.backend.core.exceptions import BusinessLogicError, BusinessValidationError
from src.backend.identity.models import (
    User, UserInfo, Role, UserRole, RefreshToken, PasswordResetToken, EmailVerificationToken,
    LoginAttempt, _sha256, )
from src.backend.identity.tasks import send_verification_email, send_password_reset_email
from src.backend.identity.tokens import JWTService


logger = logging.getLogger(__name__)

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
RESEND_COOLDOWN_SEC = 120

_DUMMY_HASH = make_password("dummy-timing-safe-password")
NAME_REGEX = re.compile(r"^[a-zA-Zа-яА-ЯёЁўЎқҚғҒҳҲъЪ’'`\s-]+$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def _get_client_ip(request) -> str:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "0.0.0.0")


def _get_user_agent(request) -> str:
    return request.META.get("HTTP_USER_AGENT", "")[:500]


def _parse_device_name(user_agent: str) -> str:
    if not user_agent:
        return "Unknown device"

    ua = parse(user_agent)

    device = ua.device.family
    os = ua.os.family
    browser = ua.browser.family

    if device == "Other":
        return f"{browser} on {os}"

    return f"{device} / {browser}"


class AuthError(BusinessLogicError):
    """Raised for all authentication business-logic failures."""
    status_code = 400

    def __init__(self, code: str, lang: str = 'uz', status_code: int = 400, **format_kwargs):
        self.lang = lang
        self.status_code = status_code
        super().__init__(code=code, **format_kwargs)


@transaction.atomic
def register_user(email: str, password: str, first_name: str, last_name: str, lang: str = 'uz') -> User:
    """
    Create user, related records, and send verification email.
    User starts inactive until email is verified.

    If user with this email exists but is not verified (is_active=False),
    delete the old account and allow re-registration.
    """
    try:
        password_validation.validate_password(password)
    except DjangoValidationError as e:
        raise BusinessValidationError(code="password_too_weak", lang=lang)

    email = email.strip().lower()

    if not EMAIL_REGEX.match(email):
        raise BusinessValidationError(code="invalid_email_format", lang=lang)

    first_name = first_name.strip()
    if not NAME_REGEX.match(first_name):
        raise BusinessValidationError(code="first_name_invalid", lang=lang)
    if len(first_name) > 30:
        raise BusinessValidationError(code="first_name_too_long", lang=lang, max_length=30)

    last_name = last_name.strip()
    if not NAME_REGEX.match(last_name):
        raise BusinessValidationError(code="last_name_invalid", lang=lang)
    if len(last_name) > 150:
        raise BusinessValidationError(code="last_name_too_long", lang=lang, max_length=150)

    existing_user = User.objects.filter(email=email).first()

    if existing_user:
        if existing_user.is_active:
            raise AuthError('email_already_registered', lang=lang)
        else:
            logger.info("Deleting unverified user for re-registration: %s", email)
            existing_user.delete()

    user = User.objects.create_user(email=email, password=password)

    UserInfo.objects.filter(user=user).update(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
    )

    student_role, _ = Role.objects.get_or_create(
        name=Role.STUDENT,
        defaults={'description': 'Default student role'}
    )
    UserRole.objects.create(user=user, role=student_role)

    raw_token, _ = EmailVerificationToken.create_for_user(user)
    user_id = str(user.id)

    logger.info("Scheduling email task for user %s", user_id)

    def send_email_task():
        logger.info("on_commit callback executing for user %s", user_id)
        send_verification_email.delay(user_id, raw_token, lang)
        logger.info("Email task queued for user %s", user_id)

    transaction.on_commit(send_email_task)

    logger.info("User registered: %s", email)
    return user


def login_user(email: str, password: str, request, lang: str = 'uz') -> dict:
    """
    Authenticate user. Returns {access_token, refresh_token}.
    Records LoginAttempt regardless of outcome.
    Enforces lockout after MAX_FAILED_ATTEMPTS failures.
    """
    ip = _get_client_ip(request)
    user_agent = _get_user_agent(request)
    email = email.lower().strip()

    ip_fail_key = f"auth:fails:{ip}"

    try:
        ip_failures = cache.incr(ip_fail_key)
        if ip_failures == 1:
            cache.touch(ip_fail_key, 900)  
    except ValueError:
        cache.set(ip_fail_key, 1, timeout=900)
        ip_failures = 1

    if ip_failures > 20:
        raise AuthError('ip_rate_limit', lang=lang, status_code=429)

    user = User.objects.filter(email=email).select_related("info").first()

    password_ok = check_password(password, user.password if user else _DUMMY_HASH)

    def _record_attempt(success, reason=None):
        LoginAttempt.objects.create(
            user=user,
            email_used=email,
            ip_address=ip,
            user_agent=user_agent,
            success=success,
            failure_reason=reason,
        )

    if not user or not password_ok:
        if user:
            with transaction.atomic():
                User.objects.filter(id=user.id).update(
                    failed_login_attempts=F('failed_login_attempts') + 1
                )

                user.refresh_from_db()
                if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                    user.locked_until = timezone.now() + timedelta(minutes=LOCKOUT_MINUTES)
                    user.save(update_fields=["locked_until"])

                    cache.delete(f"user_obj:{user.id}")
                    cache.delete(f"user_state:{user.id}")

                    logger.warning(
                        "User %s locked after %d failed attempts",
                        user.id,
                        user.failed_login_attempts
                    )

        _record_attempt(False, "bad_credentials")
        raise AuthError('invalid_credentials', lang=lang, status_code=401)

    if not user.is_active:
        _record_attempt(False, "not_verified")
        raise AuthError('email_not_verified', lang=lang, status_code=403)

    if user.is_blocked:
        _record_attempt(False, "blocked")
        raise AuthError('account_blocked', lang=lang, status_code=403)

    if user.is_locked:
        remaining = user.locked_until - timezone.now()
        minutes = max(1, int(remaining.total_seconds() / 60))
        _record_attempt(False, "locked")
        raise AuthError('account_locked', lang=lang, status_code=429, minutes=minutes)

    with transaction.atomic():
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = timezone.now()
        user.last_login_ip = ip
        user.save(update_fields=[
            "failed_login_attempts",
            "locked_until",
            "last_login_at",
            "last_login_ip"
        ])

        raw_refresh, _ = RefreshToken.create_for_user(
            user=user,
            ip_address=ip,
            user_agent=user_agent,
            device_name=_parse_device_name(user_agent),
        )

        _record_attempt(True)

    cache.delete(f"user_obj:{user.id}")
    cache.delete(f"user_state:{user.id}")

    cache.delete(ip_fail_key)

    access_token = JWTService.create_access_token(user)

    logger.info("User logged in: %s from %s", email, ip)

    return {
        "access_token": access_token,
        "refresh_token": raw_refresh,
        "token_type": "Bearer",
    }


@transaction.atomic
def refresh_access_token(raw_refresh: str, request, lang: str = 'uz') -> dict:
    """
    Rotate refresh token. If revoked token presented → token theft, revoke all.
    """
    
    logger.info(f"Refresh token rotation requested (token length: {len(raw_refresh)})")

    token_hash = _sha256(raw_refresh)
    token_obj = RefreshToken.objects.select_for_update().filter(
        token_hash=token_hash
    ).first()

    if not token_obj:
        logger.warning("Refresh token not found in database")
        raise AuthError('invalid_token', lang=lang)

    if token_obj.revoked_at is not None:
        logger.warning(
            "Revoked refresh token used for user %s — revoking all sessions",
            token_obj.user_id
        )
        RefreshToken.objects.filter(
            user=token_obj.user,
            revoked_at__isnull=True
        ).update(revoked_at=timezone.now())

        raise AuthError('token_reuse', lang=lang)

    if not token_obj.is_active:
        logger.warning("Refresh token expired for user %s", token_obj.user_id)
        raise AuthError('token_expired', lang=lang)

    user = token_obj.user
    if not user.is_active or user.is_blocked:
        raise AuthError('account_unavailable', lang=lang)

    token_obj.revoke()

    ip = _get_client_ip(request)
    user_agent = _get_user_agent(request)
    device_name = _parse_device_name(user_agent)

    raw_new, _ = RefreshToken.create_for_user(
        user=user,
        ip_address=ip,
        user_agent=user_agent,
        device_name=device_name,
    )

    access_token = JWTService.create_access_token(user)

    logger.info(
        "Refresh token rotated for user %s from device %s",
        user.id,
        device_name
    )

    return {
        "access_token": access_token,
        "refresh_token": raw_new,
        "token_type": "Bearer",
    }


def logout_user(raw_refresh: str) -> bool:
    """
    Revoke a single refresh token.
    Returns True if token was successfully revoked, False otherwise.
    """
    token_obj = RefreshToken.get_by_raw(raw_refresh)

    if not token_obj:
        logger.warning("Logout attempt with invalid token")
        return False

    if not token_obj.is_active:
        logger.info("Logout attempt with already revoked token for user %s", token_obj.user_id)
        return False

    token_obj.revoke()
    logger.info("User %s logged out from device %s", token_obj.user_id, token_obj.device_name)
    return True


def logout_all_sessions(user: User) -> int:
    """
    Revoke all active refresh tokens for a user.
    Returns the number of revoked tokens.
    """
    count = RefreshToken.objects.filter(
        user=user,
        revoked_at__isnull=True
    ).update(revoked_at=timezone.now())

    logger.info("User %s logged out from all sessions (%d tokens revoked)", user.id, count)
    return count


@transaction.atomic
def verify_email(raw_token: str, lang: str = 'uz') -> User:
    """
    Verify user's email using a token.
    Invalidates all other active tokens for this user.
    """
    token_obj = EmailVerificationToken.objects.select_for_update().filter(
        token_hash=_sha256(raw_token)
    ).first()

    if not token_obj or not token_obj.is_valid:
        raise AuthError('invalid_token', lang=lang)

    user = token_obj.user

    if user.is_active:
        raise AuthError('already_verified', lang=lang)

    EmailVerificationToken.objects.filter(
        user=user,
        verified_at__isnull=True
    ).update(verified_at=timezone.now())

    user.is_active = True
    user.save(update_fields=["is_active"])

    cache.delete(f"user_obj:{user.id}")
    cache.delete(f"user_state:{user.id}")

    logger.info("Email verified for user %s", user.email)
    return user


def resend_verification_email(email: str, lang: str = 'uz') -> None:
    """Rate-limited resend (once per 2 minutes per user)."""
    email = email.lower().strip()
    user = User.objects.filter(email=email).first()

    if not user or user.is_active:
        return

    cache_key = f"auth:verify_resend:{user.id}"

    if not cache.add(cache_key, 1, timeout=RESEND_COOLDOWN_SEC):
        raise AuthError('rate_limited', lang=lang, seconds=RESEND_COOLDOWN_SEC)

    raw_token, _ = EmailVerificationToken.create_for_user(user)
    user_id = str(user.id)

    transaction.on_commit(
        lambda: send_verification_email.delay(user_id, raw_token, lang)
    )

    logger.info("Verification email resent for user %s", user_id)


def request_password_reset(email: str, lang: str = 'uz') -> None:
    """
    Always returns without error — never confirm/deny email existence.
    Rate-limited to prevent spam.
    """
    email = email.lower().strip()
    user = User.objects.filter(email=email).first()

    if not user or not user.is_active:
        return

    cache_key = f"auth:password_reset:{user.id}"
    if not cache.add(cache_key, 1, timeout=RESEND_COOLDOWN_SEC):
        logger.info("Password reset rate limited for user %s", user.id)
        return

    raw_token, _ = PasswordResetToken.create_for_user(user)
    user_id = str(user.id)

    transaction.on_commit(
        lambda: send_password_reset_email.delay(user_id, raw_token, lang)
    )

    logger.info("Password reset requested for user %s", user_id)


@transaction.atomic
def reset_password(raw_token: str, new_password: str, lang: str = 'uz') -> User:
    """
    Reset password using a token. Invalidates all other active tokens for this user.
    """
    try:
        password_validation.validate_password(new_password)
    except DjangoValidationError:
        raise BusinessValidationError(code="password_too_weak", lang=lang)

    token_hash = _sha256(raw_token)
    token_obj = PasswordResetToken.objects.select_for_update().filter(
        token_hash=token_hash
    ).first()

    if not token_obj or not token_obj.is_valid:
        raise AuthError('invalid_token', lang=lang)

    user = token_obj.user

    PasswordResetToken.objects.filter(
        user=user,
        used_at__isnull=True
    ).update(used_at=timezone.now())

    user.set_password(new_password)
    user.save(update_fields=["password"])

    logout_all_sessions(user)

    cache.delete(f"user_obj:{user.id}")
    cache.delete(f"user_state:{user.id}")

    logger.info("Password reset completed for user %s", user.email)
    return user


@transaction.atomic
def change_password(user: User, old_password: str, new_password: str, lang: str = 'uz') -> None:
    """
    Change password for authenticated user. Requires old password.
    """
    if not check_password(old_password, user.password):
        raise AuthError('wrong_password', lang=lang)

    try:
        password_validation.validate_password(new_password, user=user)
    except DjangoValidationError:
        raise BusinessValidationError(code="password_too_weak", lang=lang)

    user.set_password(new_password)
    user.save(update_fields=["password"])

    logout_all_sessions(user)

    cache.delete(f"user_obj:{user.id}")
    cache.delete(f"user_state:{user.id}")

    logger.info("Password changed for user %s", user.email)