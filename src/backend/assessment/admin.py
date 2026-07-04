"""
Django Admin configuration for Assessment Domain
"""

from django.contrib import admin

from src.backend.assessment.domain.models.assessment import ModuleAssessment
from src.backend.assessment.domain.models.item import AssessmentItem
from src.backend.assessment.domain.models.option import AssessmentOption
from src.backend.assessment.domain.models.attempt import AssessmentAttempt
from src.backend.assessment.domain.models.response import AssessmentResponse


@admin.register(ModuleAssessment)
class ModuleAssessmentAdmin(admin.ModelAdmin):
    """Admin for ModuleAssessment."""
    list_display = ['title', 'module_id', 'passing_percentage', 'max_attempts', 'is_published']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'module_id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(AssessmentItem)
class AssessmentItemAdmin(admin.ModelAdmin):
    """Admin for AssessmentItem."""
    list_display = ['id', 'assessment_id', 'type', 'order', 'max_points']
    list_filter = ['type', 'mentor_review_required']
    search_fields = ['assessment_id', 'title']
    readonly_fields = ['id']


@admin.register(AssessmentOption)
class AssessmentOptionAdmin(admin.ModelAdmin):
    """Admin for AssessmentOption."""
    list_display = ['id', 'item_id', 'order', 'is_correct']
    list_filter = ['is_correct']
    search_fields = ['item_id', 'text']
    readonly_fields = ['id']


@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    """Admin for AssessmentAttempt."""
    list_display = ['id', 'assessment_id', 'attempt_number', 'started_at']
    list_filter = ['started_at', 'submitted_at']
    search_fields = ['assessment_id', 'enrollment_id']
    readonly_fields = ['id', 'started_at', 'submitted_at', 'graded_at']


@admin.register(AssessmentResponse)
class AssessmentResponseAdmin(admin.ModelAdmin):
    """Admin for AssessmentResponse."""
    list_display = ['id', 'attempt_id', 'item_id']
    search_fields = ['attempt_id', 'item_id']
    readonly_fields = ['id']


