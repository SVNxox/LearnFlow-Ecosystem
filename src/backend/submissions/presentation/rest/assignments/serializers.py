"""
Assignment Serializers

Serializers for assignment operations.
"""
from decimal import Decimal
from rest_framework import serializers


class CreateAssignmentSerializer(serializers.Serializer):
    """
    Serializer for creating assignments.

    POST /api/v1/assignments/
    """
    lesson_id = serializers.UUIDField(required=False, allow_null=True)
    assessment_item_id = serializers.UUIDField(required=False, allow_null=True)
    type = serializers.ChoiceField(choices=['theory', 'coding', 'project'])
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    max_score = serializers.DecimalField(max_digits=6, decimal_places=2)
    deadline_offset_days = serializers.IntegerField(required=False, allow_null=True)
    submission_types_allowed = serializers.ListField(
        child=serializers.ChoiceField(
            choices=['github_repository', 'file_upload', 'text_answer', 'external_link']
        ),
        min_length=1
    )
    allowed_file_extensions = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        help_text="Comma-separated list: .pdf,.zip,.docx"
    )
    max_file_size_mb = serializers.IntegerField(default=50, min_value=1, max_value=500)
    auto_check_enabled = serializers.BooleanField(default=False)
    auto_check_config = serializers.JSONField(required=False, allow_null=True)

    def validate(self, data):
        """Cross-field validation."""
        lesson_id = data.get('lesson_id')
        assessment_item_id = data.get('assessment_item_id')

        if not lesson_id and not assessment_item_id:
            raise serializers.ValidationError(
                "Either lesson_id or assessment_item_id must be provided"
            )

        if lesson_id and assessment_item_id:
            raise serializers.ValidationError(
                "Cannot provide both lesson_id and assessment_item_id"
            )

        return data


class AssignmentDetailSerializer(serializers.Serializer):
    """
    Serializer for assignment detail response.

    GET /api/v1/assignments/{id}/
    """
    id = serializers.UUIDField()
    lesson_id = serializers.UUIDField(allow_null=True)
    assessment_item_id = serializers.UUIDField(allow_null=True)
    type = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    max_score = serializers.DecimalField(max_digits=6, decimal_places=2)
    deadline_offset_days = serializers.IntegerField(allow_null=True)
    submission_types_allowed = serializers.ListField(child=serializers.CharField())
    allowed_file_extensions = serializers.CharField(allow_null=True)
    max_file_size_mb = serializers.IntegerField()
    auto_check_enabled = serializers.BooleanField()
    auto_check_config = serializers.JSONField()
    created_by_id = serializers.UUIDField()
    created_at = serializers.CharField()
    updated_at = serializers.CharField()

    
    total_submissions = serializers.IntegerField()
    pending_reviews = serializers.IntegerField()
    approved_count = serializers.IntegerField()
    average_score = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        allow_null=True
    )
