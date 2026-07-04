import logging
from smtplib import SMTPException
from celery import shared_task
from celery.signals import task_failure
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError, ObjectDoesNotExist
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string


logger = logging.getLogger(__name__)

VERIFICATION_EMAIL_IDEMPOTENCY_TTL = 3600 * 24
PASSWORD_RESET_EMAIL_IDEMPOTENCY_TTL = 3600

ALLOWED_EMAIL_TASKS = {
    "send_verification_email",
    "send_password_reset_email",
}


def _get_frontend_url() -> str:
    """Lazy evaluation for testing."""
    return getattr(settings, "FRONTEND_URL", "http://localhost:3000")


TRANSIENT_EMAIL_ERRORS = (
    SMTPException,
    ConnectionError,
    TimeoutError,
    OSError,
)


def _get_user_safe(user_id: str, task_name: str):
    """
    Safely load a user, ensuring protection against a missing UserInfo record.
    Returns a tuple of (user, full_name) or (None, None) if the user is not found.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        user = User.objects.select_related("info").get(id=user_id)
    except User.DoesNotExist:
        logger.error("%s: user %s not found", task_name, user_id)
        return None, None
    except ObjectDoesNotExist:
        logger.error("%s: user %s has no UserInfo", task_name, user_id)
        return None, None

    full_name = f"{user.info.first_name} {user.info.last_name}".strip() or user.email
    return user, full_name


def _send_email_with_idempotency(
        task_name: str,
        user_id: str,
        email: str,
        subject: str,
        message: str,
        html_message: str = None,
        idempotency_ttl: int = VERIFICATION_EMAIL_IDEMPOTENCY_TTL,
) -> bool:
    """
    Send an email with rate-limiting protection against duplicate sending.

    Returns:
        bool: True if the email was sent, False if it was already sent recently.

    Raises:
        DjangoValidationError: If the email is invalid (permanent error, do not retry).
        TRANSIENT_EMAIL_ERRORS: If the error is temporary (Celery will retry).
        Exception: If the error is unknown (permanent error, do not retry).
    """
    try:
        validate_email(email)
    except DjangoValidationError:
        logger.error(
            "%s: invalid email address '%s' for user %s",
            task_name,
            email,
            user_id
        )
        raise

    idempotency_key = f"email_sent:{task_name}:{user_id}"

    if not cache.add(idempotency_key, True, timeout=idempotency_ttl):
        logger.info(
            "%s: email already sent to user %s (idempotency), skipping",
            task_name,
            user_id
        )
        return False

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info("%s: email sent to %s", task_name, email)
        return True

    except TRANSIENT_EMAIL_ERRORS as exc:
        cache.delete(idempotency_key)
        logger.warning(
            "%s: transient error sending email to %s: %s. Will retry.",
            task_name,
            email,
            str(exc)
        )
        raise

    except Exception as exc:
        logger.error(
            "%s: permanent error sending email to %s: %s",
            task_name,
            email,
            str(exc),
            exc_info=True
        )
        return False


def _send_localized_email(
        task_name: str,
        user,
        full_name: str,
        raw_token: str,
        lang: str,
        template_name: str,
        url_path: str,
        subject_key: str,
        idempotency_ttl: int = VERIFICATION_EMAIL_IDEMPOTENCY_TTL,
):
    """
    Base function for sending localized emails.

    Args:
        task_name: Name of the Celery task (for logging and idempotency key)
        user: User object (must have .email attribute)
        full_name: User's full name for personalization
        raw_token: Raw token for URL generation
        lang: Language code ('uz', 'ru', 'en')
        template_name: Base template name (e.g., "emails/verification")
        url_path: URL path for token (e.g., "/verify-email")
        subject_key: Key for subject translation (e.g., "verification")
        idempotency_ttl: TTL for idempotency key in seconds

    Raises:
        DjangoValidationError: If email is invalid
        TRANSIENT_EMAIL_ERRORS: If email sending fails temporarily
        Exception: If email sending fails permanently
    """
    token_url = f"{_get_frontend_url()}{url_path}?token={raw_token}"

    subject_translations = {
        'uz': {
            'verification': "LearnFlow email manzilingizni tasdiqlang",
            'password_reset': "LearnFlow parolni tiklash",
        },
        'ru': {
            'verification': "Подтвердите ваш email в LearnFlow",
            'password_reset': "Сброс пароля в LearnFlow",
        },
        'en': {
            'verification': "Verify your LearnFlow email",
            'password_reset': "Reset your LearnFlow password",
        },
    }
    subject = subject_translations.get(lang, {}).get(
        subject_key,
        subject_translations['en'][subject_key]
    )

    context = {
        "full_name": full_name,
        "token_url": token_url,
    }

    try:
        message = render_to_string(f"{template_name}_{lang}.txt", context)
    except TemplateDoesNotExist:
        try:
            message = render_to_string(f"{template_name}_en.txt", context)
        except TemplateDoesNotExist:
            logger.error(
                "%s: template %s_en.txt not found",
                task_name,
                template_name
            )
            raise

    try:
        html_message = render_to_string(f"{template_name}_{lang}.html", context)
    except TemplateDoesNotExist:
        html_message = None

    _send_email_with_idempotency(
        task_name=task_name,
        user_id=str(user.id),
        email=user.email,
        subject=subject,
        message=message,
        html_message=html_message,
        idempotency_ttl=idempotency_ttl,
    )


@shared_task(
    bind=True,
    max_retries=5,
    rate_limit="100/m",
    autoretry_for=TRANSIENT_EMAIL_ERRORS,
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def send_verification_email(self, user_id: str, raw_token: str, lang: str = 'uz'):
    """Send email verification link to user."""
    logger.info("send_verification_email task started for user %s", user_id)

    user, full_name = _get_user_safe(user_id, "send_verification_email")
    if user is None:
        return

    if user.is_active:
        logger.info("User %s already active, skipping", user_id)
        return

    _send_localized_email(
        task_name="send_verification_email",
        user=user,
        full_name=full_name,
        raw_token=raw_token,
        lang=lang,
        template_name="emails/verification",
        url_path="/verify-email",
        subject_key="verification",
        idempotency_ttl=VERIFICATION_EMAIL_IDEMPOTENCY_TTL,
    )

    logger.info("send_verification_email task completed for user %s", user_id)


@shared_task(
    bind=True,
    max_retries=5,
    rate_limit="100/m",
    autoretry_for=TRANSIENT_EMAIL_ERRORS,
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def send_password_reset_email(self, user_id: str, raw_token: str, lang: str = 'uz'):
    """Send password reset link to user."""
    logger.info("send_password_reset_email task started for user %s", user_id)

    user, full_name = _get_user_safe(user_id, "send_password_reset_email")
    if user is None:
        return

    _send_localized_email(
        task_name="send_password_reset_email",
        user=user,
        full_name=full_name,
        raw_token=raw_token,
        lang=lang,
        template_name="emails/password_reset",
        url_path="/password-reset/confirm",
        subject_key="password_reset",
        idempotency_ttl=PASSWORD_RESET_EMAIL_IDEMPOTENCY_TTL,
    )

    logger.info("send_password_reset_email task completed for user %s", user_id)


@task_failure.connect
def handle_email_task_failure(sender, task_id, exception, traceback, **kwargs):
    """
    Handler for email task failures.
    """
    if sender.name not in ALLOWED_EMAIL_TASKS:
        return

    logger.error(
        "%s task %s failed permanently: %s",
        sender.name,
        task_id,
        str(exception),
        exc_info=traceback
    )

    
    
    
    
    