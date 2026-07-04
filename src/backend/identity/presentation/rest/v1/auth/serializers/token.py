"""
identity/presentation/rest/v1/auth/serializers/token.py

Token refresh endpoint serializers.
"""
from rest_framework import serializers


class TokenRefreshRequestSerializer(serializers.Serializer):
    """POST /api/v1/identity/auth/token/refresh/ request body."""

    refresh_token = serializers.CharField(
        help_text='Valid refresh token from login or previous refresh'
    )


class TokenResponseSerializer(serializers.Serializer):
    """
    Token response schema.

    Used by:
    - POST /api/v1/identity/auth/login/
    - POST /api/v1/identity/auth/token/refresh/
    """

    access_token = serializers.CharField(
        help_text='JWT access token (15 min lifetime, RS256)'
    )
    refresh_token = serializers.CharField(
        help_text='Refresh token (30 days lifetime, rotates on each refresh)'
    )
    token_type = serializers.CharField(
        default='Bearer',
        help_text='Token type (always Bearer)'
    )
