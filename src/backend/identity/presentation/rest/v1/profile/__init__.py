"""
identity/presentation/rest/v1/profile/__init__.py

Profile-related views.
"""
from .me import MeView
from .change_password import ChangePasswordView
from .settings import UserSettingsView
from .sessions import ActiveSessionsView, RevokeSessionView

__all__ = [
    'MeView',
    'ChangePasswordView',
    'UserSettingsView',
    'ActiveSessionsView',
    'RevokeSessionView',
]
