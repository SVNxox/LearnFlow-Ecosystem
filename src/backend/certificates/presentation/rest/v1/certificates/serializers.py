"""
Certificate serializers
"""

from rest_framework import serializers
from src.backend.certificates.domain.models import Certificate


class CertificateListSerializer(serializers.ModelSerializer):
    """Serializer for certificate list view."""

    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Certificate
        fields = [
            'id',
            'certificate_number',
            'verification_code',
            'course_name_snapshot',
            'status',
            'status_display',
            'completion_date',
            'issued_at',
            'pdf_url',
        ]
        read_only_fields = fields


class CertificateDetailSerializer(serializers.ModelSerializer):
    """Serializer for certificate detail view."""

    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    template_name = serializers.CharField(
        source='template.name',
        read_only=True
    )

    class Meta:
        model = Certificate
        fields = [
            'id',
            'certificate_number',
            'verification_code',
            'student_full_name_snapshot',
            'course_name_snapshot',
            'course_description_snapshot',
            'final_score',
            'completion_date',
            'issued_at',
            'status',
            'status_display',
            'pdf_url',
            'pdf_generated_at',
            'template_name',
            'revoked_at',
            'revoked_reason',
        ]
        read_only_fields = fields


class VerifyCertificateSerializer(serializers.Serializer):
    """Serializer for certificate verification response."""

    valid = serializers.BooleanField()
    status = serializers.CharField()
    certificate_number = serializers.CharField()
    verification_code = serializers.CharField(required=False)
    student_name = serializers.CharField(required=False)
    course_name = serializers.CharField(required=False)
    course_description = serializers.CharField(required=False, allow_null=True)
    final_score = serializers.FloatField(required=False, allow_null=True)
    completion_date = serializers.CharField(required=False)
    issued_at = serializers.CharField(required=False)
    issued_by = serializers.CharField(required=False)
    message = serializers.CharField(required=False)
    revoked_reason = serializers.CharField(required=False)
    revoked_at = serializers.DateTimeField(required=False)
