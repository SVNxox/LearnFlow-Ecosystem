"""
Enrollment Domain admin interface.
"""

from django.contrib import admin
from src.backend.enrollment.domain.models import CourseEnrollment


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course_id', 'status', 'delivery_format', 'enrolled_at']
    list_filter = ['status', 'delivery_format', 'enrolled_at']
    search_fields = ['user__email', 'course_id']
    readonly_fields = ['id', 'enrolled_at', 'completed_at', 'dropped_at']
    date_hierarchy = 'enrolled_at'
