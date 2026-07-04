"""
CheckAccess serializer — GET /api/v1/enrollment/enrollments/{id}/check-access/
"""

from rest_framework import serializers


class CheckAccessRequestSerializer(serializers.Serializer):
    """Request serializer for access check."""

    content_id = serializers.UUIDField(
        required=True,
        help_text="UUID of content to check access for"
    )


class CheckAccessResponseSerializer(serializers.Serializer):
    """Response serializer for access check."""

    can_access = serializers.BooleanField()
    reason = serializers.CharField(allow_blank=True)
