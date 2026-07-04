"""
Django Admin configuration for Progress Domain
"""

from django.contrib import admin
from django.utils.html import format_html

from src.backend.progress.domain.models.course_progress import CourseProgress
from src.backend.progress.domain.models.module_progress import ModuleProgress
from src.backend.progress.domain.models.lesson_progress import LessonProgress


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    """Admin for CourseProgress."""

    list_display = [
        'id',
        'enrollment_link',
        'user_email',
        'cached_percentage',
        'status',
        'started_at',
        'completed_at',
    ]

    list_filter = [
        'status',
        'delivery_format',
        'started_at',
        'completed_at',
    ]

    search_fields = [
        'enrollment_id',
        'user_id',
        'course_id',
    ]

    readonly_fields = [
        'id',
        'enrollment_id',
        'user_id',
        'course_id',
        'delivery_format',
        'is_sequential',
        'status',
        'total_modules_count',
        'completed_modules_count',
        'cached_percentage',
        'started_at',
        'completed_at',
        'last_activity_at',
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'enrollment_id', 'user_id', 'course_id')
        }),
        ('Progress', {
            'fields': (
                'status',
                'delivery_format',
                'is_sequential',
                'total_modules_count',
                'completed_modules_count',
                'cached_percentage',
            )
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at', 'last_activity_at', 'created_at', 'updated_at')
        }),
    )

    def enrollment_link(self, obj):
        return format_html(
            '<a href="/admin/enrollment/courseenrollment/{}/change/">{}</a>',
            obj.enrollment_id,
            str(obj.enrollment_id)[:8]
        )
    enrollment_link.short_description = 'Enrollment'

    def user_email(self, obj):
        return str(obj.user_id)[:8]
    user_email.short_description = 'User'


@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    """Admin for ModuleProgress."""

    list_display = [
        'id',
        'enrollment_link',
        'module_id_short',
        'status',
        'completed_lessons_ratio',
        'completed_at',
    ]

    list_filter = [
        'status',
        'is_stale',
        'assessment_required',
        'assessment_passed',
        'completed_at',
    ]

    search_fields = [
        'enrollment_id',
        'module_id',
        'course_id',
    ]

    readonly_fields = [
        'id',
        'enrollment_id',
        'module_id',
        'course_id',
        'module_order',
        'status',
        'total_lessons_count',
        'completed_lessons_count',
        'assessment_required',
        'assessment_passed',
        'assessment_passed_at',
        'is_stale',
        'unlocked_at',
        'completed_at',
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'enrollment_id', 'module_id', 'course_id', 'module_order')
        }),
        ('Progress', {
            'fields': (
                'status',
                'total_lessons_count',
                'completed_lessons_count',
            )
        }),
        ('Assessment', {
            'fields': (
                'assessment_required',
                'assessment_passed',
                'assessment_passed_at',
            )
        }),
        ('Timestamps', {
            'fields': ('is_stale', 'unlocked_at', 'completed_at', 'created_at', 'updated_at')
        }),
    )

    def enrollment_link(self, obj):
        return format_html(
            '<a href="/admin/enrollment/courseenrollment/{}/change/">{}</a>',
            obj.enrollment_id,
            str(obj.enrollment_id)[:8]
        )
    enrollment_link.short_description = 'Enrollment'

    def module_id_short(self, obj):
        return str(obj.module_id)[:8]
    module_id_short.short_description = 'Module'

    def completed_lessons_ratio(self, obj):
        return f"{obj.completed_lessons_count}/{obj.total_lessons_count}"
    completed_lessons_ratio.short_description = 'Lessons'


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    """Admin for LessonProgress."""

    list_display = [
        'id',
        'enrollment_link',
        'lesson_id_short',
        'status',
        'completed_at',
        'completion_source',
    ]

    list_filter = [
        'status',
        'completion_source',
        'homework_required',
        'homework_submitted',
        'completed_at',
    ]

    search_fields = [
        'enrollment_id',
        'lesson_id',
        'module_id',
        'course_id',
    ]

    readonly_fields = [
        'id',
        'enrollment_id',
        'lesson_id',
        'module_id',
        'course_id',
        'lesson_order',
        'module_order',
        'status',
        'completion_source',
        'required_content_count',
        'viewed_required_count',
        'homework_required',
        'homework_submitted',
        'homework_submitted_at',
        'completed_at',
        'override_by_id',
        'override_reason',
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'enrollment_id', 'lesson_id', 'module_id', 'course_id')
        }),
        ('Order', {
            'fields': ('lesson_order', 'module_order')
        }),
        ('Status', {
            'fields': ('status', 'completed_at', 'completion_source')
        }),
        ('Content Progress', {
            'fields': ('required_content_count', 'viewed_required_count')
        }),
        ('Homework', {
            'fields': ('homework_required', 'homework_submitted', 'homework_submitted_at')
        }),
        ('Override', {
            'fields': ('override_by_id', 'override_reason'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def enrollment_link(self, obj):
        return format_html(
            '<a href="/admin/enrollment/courseenrollment/{}/change/">{}</a>',
            obj.enrollment_id,
            str(obj.enrollment_id)[:8]
        )
    enrollment_link.short_description = 'Enrollment'

    def lesson_id_short(self, obj):
        return str(obj.lesson_id)[:8]
    lesson_id_short.short_description = 'Lesson'
