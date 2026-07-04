"""
DropEnrollment serializer — POST /api/v1/enrollment/enrollments/{id}/drop/
"""

from rest_framework import serializers


class DropEnrollmentSerializer(serializers.Serializer):
    """Serializer for dropping enrollment."""

    reason = serializers.CharField(
        required=True,
        max_length=500,
        help_text="Reason for dropping enrollment"
    )

    def validate_reason(self, value):
        """Validate reason is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Reason cannot be empty")
        return value.strip()
