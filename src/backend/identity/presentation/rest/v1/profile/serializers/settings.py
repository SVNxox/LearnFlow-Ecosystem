"""
identity/presentation/rest/v1/profile/serializers/settings.py

User settings serializers.
"""
from rest_framework import serializers
from src.backend.identity.models import UserSettings


class UserSettingsSerializer(serializers.ModelSerializer):
    """
    GET/PATCH /api/v1/identity/profile/me/settings/

    User notification and UI preferences.
    """

    class Meta:
        model = UserSettings
        fields = [
            "language", "timezone",
            "notify_email", "notify_telegram", "notify_web",
            "notify_deadlines", "notify_grades", "notify_mentor_comments",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]
