"""
EnrollmentDetail serializer — GET /api/v1/enrollment/enrollments/{id}/
"""

from rest_framework import serializers

from src.backend.enrollment.domain.models import CourseEnrollment


class EnrollmentDetailSerializer(serializers.ModelSerializer):
    """Serializer for enrollment detail view."""

    user_id = serializers.UUIDField(source='user.id', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    can_access = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = CourseEnrollment
        fields = [
            'id',
            'user_id',
            'user_email',
            'course_id',
            'status',
            'delivery_format',
            'access_level',
            'payment_id',
            'payment_status',
            'enrolled_at',
            'start_date',
            'end_date',
            'suspended_at',
            'suspended_reason',
            'dropped_at',
            'dropped_reason',
            'completed_at',
            'can_access',
            'is_expired',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_can_access(self, obj: CourseEnrollment) -> bool:
        """Check if enrollment allows access."""
        return obj.can_access_course()

    def get_is_expired(self, obj: CourseEnrollment) -> bool:
        """Check if enrollment is expired."""
        return obj.is_expired()
