"""
identity/presentation/rest/v1/auth/serializers/password.py

Password reset endpoint serializers.
"""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class PasswordResetRequestSerializer(serializers.Serializer):
    """POST /api/v1/identity/auth/password-reset/ request body."""

    email = serializers.EmailField(
        help_text='Email address to send password reset link to'
    )

    def validate_email(self, value):
        """Normalize email to lowercase."""
        return value.lower().strip()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """POST /api/v1/identity/auth/password-reset/confirm/ request body."""

    token = serializers.CharField(
        help_text='Password reset token from the reset link'
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128,
        style={'input_type': 'password'},
        help_text='New password (min 8 characters, validated against Django password validators)'
    )

    def validate_new_password(self, value):
        """Validate password against Django password validators."""
        validate_password(value)
        return value
