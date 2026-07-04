"""
identity/presentation/rest/v1/auth/serializers/email.py

Email verification endpoint serializers.
"""
from rest_framework import serializers


class EmailVerifyRequestSerializer(serializers.Serializer):
    """GET /api/v1/identity/auth/verify-email/ query parameters."""

    token = serializers.CharField(
        help_text='Email verification token from the verification link'
    )


class EmailResendRequestSerializer(serializers.Serializer):
    """POST /api/v1/identity/auth/verify-email/resend/ request body."""

    email = serializers.EmailField(
        help_text='Email address to resend verification link to'
    )

    def validate_email(self, value):
        """Normalize email to lowercase."""
        return value.lower().strip()
