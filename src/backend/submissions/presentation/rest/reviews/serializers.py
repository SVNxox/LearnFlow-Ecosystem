"""
Review Serializers

Serializers for mentor review operations.
"""
from rest_framework import serializers


class SubmitReviewSerializer(serializers.Serializer):
    """
    Serializer for submitting review.

    POST /api/v1/reviews/
    """
    submission_id = serializers.UUIDField()
    revision_id = serializers.UUIDField()
    score = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=0)
    feedback = serializers.CharField()
    status = serializers.ChoiceField(
        choices=['changes_requested', 'approved', 'rejected']
    )


class PendingReviewSerializer(serializers.Serializer):
    """
    Serializer for pending review list.

    GET /api/v1/reviews/pending/
    """
    id = serializers.UUIDField()
    assignment_id = serializers.UUIDField()
    assignment_title = serializers.CharField()
    assignment_type = serializers.CharField()
    assignment_max_score = serializers.DecimalField(max_digits=6, decimal_places=2)
    student_id = serializers.UUIDField()
    enrollment_id = serializers.UUIDField()
    status = serializers.CharField()
    current_revision_number = serializers.IntegerField()
    last_submitted_at = serializers.CharField()
    deadline = serializers.CharField(allow_null=True)
    is_overdue = serializers.BooleanField()
    waiting_days = serializers.IntegerField()


class ReviewResponseSerializer(serializers.Serializer):
    """
    Serializer for review response.

    Response after submitting review.
    """
    id = serializers.UUIDField()
    submission_id = serializers.UUIDField()
    revision_id = serializers.UUIDField()
    mentor_id = serializers.UUIDField()
    score = serializers.DecimalField(max_digits=6, decimal_places=2)
    max_score = serializers.DecimalField(max_digits=6, decimal_places=2)
    feedback = serializers.CharField()
    status = serializers.CharField()
    reviewed_at = serializers.CharField()
