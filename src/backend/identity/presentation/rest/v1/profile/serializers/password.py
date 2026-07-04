"""
identity/presentation/rest/v1/profile/serializers/password.py

Change password serializers.
"""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class ChangePasswordSerializer(serializers.Serializer):
    """POST /api/v1/identity/profile/me/password/ request body."""

    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text='Current password'
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
