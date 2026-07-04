"""
identity/presentation/rest/v1/auth/serializers/logout.py

Logout endpoint serializers.
"""
from rest_framework import serializers


class LogoutRequestSerializer(serializers.Serializer):
    """POST /api/v1/identity/auth/logout/ request body."""

    refresh_token = serializers.CharField(
        help_text='Refresh token to revoke'
    )
