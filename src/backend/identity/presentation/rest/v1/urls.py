"""
Identity Domain API v1 URLs.
"""
from django.urls import path, include

from .auth import (
    LoginView,
    RegisterView,
    TokenRefreshView,
    LogoutView,
    LogoutAllView,
    EmailVerifyView,
    EmailResendView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)
from .profile import (
    MeView,
    ChangePasswordView,
    UserSettingsView,
    ActiveSessionsView,
    RevokeSessionView,
)

app_name = 'identity'

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='auth-token-refresh'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/logout/all/', LogoutAllView.as_view(), name='auth-logout-all'),

    path('auth/verify-email/', EmailVerifyView.as_view(), name='auth-verify-email'),
    path('auth/verify-email/resend/', EmailResendView.as_view(), name='auth-verify-resend'),

    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='auth-password-reset'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),

    path('profile/me/', MeView.as_view(), name='profile-me'),
    path('profile/me/password/', ChangePasswordView.as_view(), name='profile-change-password'),
    path('profile/me/settings/', UserSettingsView.as_view(), name='profile-settings'),

    path('profile/me/sessions/', ActiveSessionsView.as_view(), name='profile-sessions'),
    path('profile/me/sessions/<uuid:session_id>/', RevokeSessionView.as_view(), name='profile-session-revoke'),

    path('admin/', include('src.backend.identity.presentation.rest.v1.admin.urls')),
]
