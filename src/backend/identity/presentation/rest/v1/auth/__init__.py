"""
Auth-related views.
"""
from .login import LoginView
from .register import RegisterView
from .token_refresh import TokenRefreshView
from .logout import LogoutView, LogoutAllView
from .verify_email import EmailVerifyView, EmailResendView
from .password_reset import PasswordResetRequestView, PasswordResetConfirmView

__all__ = [
    'LoginView',

    'RegisterView',

    'TokenRefreshView',

    'LogoutView',
    'LogoutAllView',

    'EmailVerifyView',
    'EmailResendView',

    'PasswordResetRequestView',
    'PasswordResetConfirmView',
]
