"""
Django Admin configuration for Submissions Domain
"""

from django.contrib import admin

from src.backend.submissions.domain.models.assignment import Assignment
from src.backend.submissions.domain.models.submission import Submission
from src.backend.submissions.domain.models.revision import SubmissionRevision
from src.backend.submissions.domain.models.file import SubmissionFile
from src.backend.submissions.domain.models.review import SubmissionReview


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """Admin for Assignment."""
    list_display = ['title', 'lesson_id', 'max_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'lesson_id', 'assessment_item_id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """Admin for Submission."""
    list_display = ['id', 'assignment_id', 'student_id', 'status', 'final_score', 'reviewed_at']
    list_filter = ['status', 'reviewed_at']
    search_fields = ['assignment_id', 'student_id', 'enrollment_id']
    readonly_fields = ['id', 'created_at', 'reviewed_at']


@admin.register(SubmissionRevision)
class SubmissionRevisionAdmin(admin.ModelAdmin):
    """Admin for SubmissionRevision."""
    list_display = ['id', 'submission', 'revision_number', 'submitted_at']
    search_fields = ['submission__id']
    readonly_fields = ['id', 'submitted_at']


@admin.register(SubmissionFile)
class SubmissionFileAdmin(admin.ModelAdmin):
    """Admin for SubmissionFile."""
    list_display = ['file_name', 'revision_id', 'file_size_bytes', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['file_name', 'revision_id']
    readonly_fields = ['id', 'uploaded_at']


@admin.register(SubmissionReview)
class SubmissionReviewAdmin(admin.ModelAdmin):
    """Admin for SubmissionReview."""
    list_display = ['id', 'submission', 'mentor_id', 'score', 'reviewed_at']
    list_filter = ['reviewed_at', 'status']
    search_fields = ['submission__id', 'mentor_id']
    readonly_fields = ['id', 'reviewed_at']


