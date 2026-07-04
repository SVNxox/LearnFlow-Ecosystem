"""
identity/presentation/rest/v1/auth/serializers/register.py

Register endpoint serializers.
"""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class RegisterRequestSerializer(serializers.Serializer):
    """POST /api/v1/identity/auth/register/ request body."""

    email = serializers.EmailField(
        max_length=254,
        help_text='User email address (will be normalized to lowercase)'
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128,
        style={'input_type': 'password'},
        help_text='Password (min 8 characters, validated against Django password validators)'
    )
    first_name = serializers.CharField(
        max_length=100,
        help_text='User first name'
    )
    last_name = serializers.CharField(
        max_length=100,
        help_text='User last name'
    )

    def validate_email(self, value):
        """Normalize email to lowercase."""
        return value.lower().strip()

    def validate_password(self, value):
        """Validate password against Django password validators."""
        validate_password(value)
        return value
