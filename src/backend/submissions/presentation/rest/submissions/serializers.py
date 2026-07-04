"""
Submission Serializers

Serializers for submission operations.
"""
from rest_framework import serializers


class CreateSubmissionSerializer(serializers.Serializer):
    """
    Serializer for creating submission with first revision.

    POST /api/v1/submissions/
    """
    assignment_id = serializers.UUIDField()
    enrollment_id = serializers.UUIDField()
    submission_type = serializers.ChoiceField(
        choices=['github_repository', 'file_upload', 'text_answer', 'external_link'],
        default='text_answer'
    )
    payload = serializers.JSONField(default=dict)
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_payload(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("payload must be a JSON object")
        return value

class SubmitRevisionSerializer(serializers.Serializer):
    """
    Serializer for submitting new revision.

    POST /api/v1/submissions/{id}/revisions/
    """
    submission_type = serializers.ChoiceField(
        choices=['github_repository', 'file_upload', 'text_answer', 'external_link']
    )
    payload = serializers.JSONField()
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_payload(self, value):
        """Validate payload structure based on submission_type."""
        
        if not isinstance(value, dict):
            raise serializers.ValidationError("payload must be a JSON object")
        return value


class MySubmissionSerializer(serializers.Serializer):
    """
    Serializer for student's submission list.

    GET /api/v1/submissions/my/
    """
    id = serializers.UUIDField()
    assignment_id = serializers.UUIDField()
    assignment_title = serializers.CharField()
    assignment_type = serializers.CharField()
    assignment_max_score = serializers.DecimalField(max_digits=6, decimal_places=2)
    status = serializers.CharField()
    current_revision_number = serializers.IntegerField()
    deadline = serializers.CharField(allow_null=True)
    first_submitted_at = serializers.CharField(allow_null=True)
    last_submitted_at = serializers.CharField(allow_null=True)
    reviewed_at = serializers.CharField(allow_null=True)
    final_score = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        allow_null=True
    )
    is_overdue = serializers.BooleanField()


class SubmissionFileSerializer(serializers.Serializer):
    """File metadata."""
    id = serializers.UUIDField()
    file_key = serializers.CharField()
    file_name = serializers.CharField()
    file_size = serializers.IntegerField()
    mime_type = serializers.CharField()
    scan_status = serializers.CharField()
    uploaded_at = serializers.CharField()


class AutoCheckSerializer(serializers.Serializer):
    """Auto check result."""
    id = serializers.UUIDField()
    status = serializers.CharField()
    score = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        allow_null=True
    )
    report = serializers.JSONField()
    started_at = serializers.CharField(allow_null=True)
    completed_at = serializers.CharField(allow_null=True)


class ReviewSerializer(serializers.Serializer):
    """Review details."""
    id = serializers.UUIDField()
    mentor_id = serializers.UUIDField()
    score = serializers.DecimalField(max_digits=6, decimal_places=2)
    max_score = serializers.DecimalField(max_digits=6, decimal_places=2)
    feedback = serializers.CharField()
    status = serializers.CharField()
    reviewed_at = serializers.CharField()


class RevisionSerializer(serializers.Serializer):
    """Revision with files, auto checks, and review."""
    id = serializers.UUIDField()
    revision_number = serializers.IntegerField()
    submission_type = serializers.CharField()
    payload = serializers.JSONField()
    notes = serializers.CharField()
    submitted_at = serializers.CharField()
    files = SubmissionFileSerializer(many=True)
    auto_check = AutoCheckSerializer(allow_null=True)
    review = ReviewSerializer(allow_null=True)


class SubmissionDetailSerializer(serializers.Serializer):
    """
    Complete submission details.

    GET /api/v1/submissions/{id}/
    """
    id = serializers.UUIDField()
    assignment_id = serializers.UUIDField()
    assignment_title = serializers.CharField()
    assignment_description = serializers.CharField()
    assignment_type = serializers.CharField()
    assignment_max_score = serializers.DecimalField(max_digits=6, decimal_places=2)
    enrollment_id = serializers.UUIDField()
    student_id = serializers.UUIDField()
    status = serializers.CharField()
    current_revision_number = serializers.IntegerField()
    deadline = serializers.CharField(allow_null=True)
    first_submitted_at = serializers.CharField(allow_null=True)
    last_submitted_at = serializers.CharField(allow_null=True)
    reviewed_at = serializers.CharField(allow_null=True)
    final_score = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        allow_null=True
    )
    is_overdue = serializers.BooleanField()
    created_at = serializers.CharField()
    updated_at = serializers.CharField()
    revisions = RevisionSerializer(many=True)
