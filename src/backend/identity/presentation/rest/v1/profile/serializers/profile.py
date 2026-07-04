"""
identity/presentation/rest/v1/profile/serializers/profile.py

User profile serializers.
"""
from rest_framework import serializers
from src.backend.identity.models import User, UserInfo


class UserInfoSerializer(serializers.ModelSerializer):
    """Nested UserInfo serializer."""

    class Meta:
        model = UserInfo
        fields = [
            "first_name", "last_name", "avatar_url", "phone", "bio",
            "date_of_birth", "telegram_id", "updated_at"
        ]
        read_only_fields = ["updated_at"]


class UserProfileSerializer(serializers.ModelSerializer):
    """
    GET /api/v1/identity/profile/me/ response.

    Full authenticated-user profile with nested info and settings.
    No sensitive fields (password_hash, last_login_ip, token_hash).
    """

    info = UserInfoSerializer(read_only=True)
    settings = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "is_active", "is_blocked",
            "last_login_at", "created_at",
            "info", "settings", "roles",
        ]
        read_only_fields = fields

    def get_settings(self, obj):
        """Return nested settings data."""
        from .settings import UserSettingsSerializer
        return UserSettingsSerializer(obj.settings).data

    def get_roles(self, obj):
        """Return list of active role names."""
        active_roles = obj.user_roles.filter(is_active=True).select_related("role")
        return [ur.role.name for ur in active_roles]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    PATCH /api/v1/identity/profile/me/ request body.

    Updates UserInfo fields via nested write.
    """

    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_null=True,
        allow_blank=True
    )
    bio = serializers.CharField(
        max_length=1000,
        required=False,
        allow_null=True,
        allow_blank=True
    )
    date_of_birth = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = UserInfo
        fields = ["first_name", "last_name", "phone", "bio", "date_of_birth"]
