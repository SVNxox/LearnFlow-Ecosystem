"""
EnrollmentCreate serializer — POST /api/v1/enrollment/enrollments/
"""

from rest_framework import serializers

from src.backend.enrollment.domain.models import CourseEnrollment


class EnrollmentCreateSerializer(serializers.Serializer):
    """Serializer for creating enrollment."""

    course_id = serializers.UUIDField(required=True)
    delivery_format = serializers.ChoiceField(
        choices=[
            CourseEnrollment.DeliveryFormat.ONLINE,
            CourseEnrollment.DeliveryFormat.OFFLINE,
            CourseEnrollment.DeliveryFormat.HYBRID,
        ],
        required=True
    )
    access_level = serializers.ChoiceField(
        choices=[
            CourseEnrollment.AccessLevel.FULL,
            CourseEnrollment.AccessLevel.LIMITED,
            CourseEnrollment.AccessLevel.PREVIEW,
        ],
        required=False,
        default=CourseEnrollment.AccessLevel.FULL
    )

    def validate(self, attrs):
        """Additional validation."""
        
        return attrs
