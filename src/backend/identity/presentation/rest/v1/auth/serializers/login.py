"""
Login endpoint serializers.
"""
from rest_framework import serializers


class LoginRequestSerializer(serializers.Serializer):
    """POST /api/v1/identity/auth/login/ request body."""

    email = serializers.EmailField(
        max_length=254,
        help_text='User email address'
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text='User password'
    )

    def validate_email(self, value):
        """Normalize email to lowercase."""
        return value.lower().strip()


class LoginResponseSerializer(serializers.Serializer):
    """POST /api/v1/identity/auth/login/ response body."""

    access_token = serializers.CharField(
        help_text='JWT access token (15 min lifetime, RS256)'
    )
    refresh_token = serializers.CharField(
        help_text='Refresh token (30 days lifetime)'
    )
    token_type = serializers.CharField(
        default='Bearer',
        help_text='Token type (always Bearer)'
    )
