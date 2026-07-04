"""
EnrollmentList serializer — GET /api/v1/enrollment/enrollments/
"""

from rest_framework import serializers

from src.backend.enrollment.domain.models import CourseEnrollment
from src.backend.learning.domain.models.course import Course


class EnrollmentListSerializer(serializers.ModelSerializer):
    """Serializer for enrollment list view."""

    user_id = serializers.UUIDField(source='user.id', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()
    can_access = serializers.SerializerMethodField()

    class Meta:
        model = CourseEnrollment
        fields = [
            'id',
            'user_id',
            'user_email',
            'user_name',
            'course_id',
            'course_title',
            'status',
            'delivery_format',
            'access_level',
            'payment_status',
            'enrolled_at',
            'completed_at',
            'can_access',
        ]
        read_only_fields = fields

    def get_user_name(self, obj: CourseEnrollment) -> str:
        """Get user's full name or email."""
        if hasattr(obj.user, 'info'):
            full_name = f"{obj.user.info.first_name} {obj.user.info.last_name}".strip()
            if full_name:
                return full_name
        return obj.user.email

    def get_course_title(self, obj: CourseEnrollment) -> str:
        """Get course title from Learning domain."""
        try:
            course = Course.objects.only('title').get(id=obj.course_id)
            return course.title
        except Course.DoesNotExist:
            return f"Course {obj.course_id}"

    def get_can_access(self, obj: CourseEnrollment) -> bool:
        """Check if enrollment allows access."""
        return obj.can_access_course()
