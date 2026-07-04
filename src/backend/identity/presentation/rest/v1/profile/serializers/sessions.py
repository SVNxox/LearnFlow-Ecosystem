"""
identity/presentation/rest/v1/profile/serializers/sessions.py

Active sessions serializers.
"""
from rest_framework import serializers
from src.backend.identity.models import RefreshToken


class ActiveSessionSerializer(serializers.ModelSerializer):
    """
    GET /api/v1/identity/profile/me/sessions/ response.

    Lists all active refresh token sessions for the authenticated user.
    """

    class Meta:
        model = RefreshToken
        fields = ["id", "device_name", "ip_address", "created_at", "expires_at"]
        read_only_fields = fields
