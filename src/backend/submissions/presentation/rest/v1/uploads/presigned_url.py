"""
POST /api/v1/submissions/uploads/presigned-url/

Generate presigned URL for direct S3 upload.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, serializers
from drf_spectacular.utils import extend_schema, OpenApiParameter
from src.backend.shared.infrastructure.storage import get_s3_client
import uuid
import os
from typing import Dict, Any


class PresignedUploadRequestSerializer(serializers.Serializer):
    """Request payload for presigned URL generation."""

    filename = serializers.CharField(
        max_length=255,
        help_text="Original filename (e.g., 'homework.pdf')"
    )
    content_type = serializers.CharField(
        max_length=100,
        help_text="MIME type (e.g., 'application/pdf', 'image/png')"
    )
    submission_id = serializers.UUIDField(
        help_text="Submission ID to associate file with"
    )

    def validate_content_type(self, value: str) -> str:
        """Validate content type is allowed."""
        allowed_types = [
            
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/webp',
            
            'application/zip',
            'application/x-rar-compressed',
            'application/x-7z-compressed',
            
            'text/plain',
            'text/x-python',
            'text/javascript',
            'application/json',
        ]

        if value not in allowed_types:
            raise serializers.ValidationError(
                f"Content type '{value}' is not allowed. "
                f"Allowed types: {', '.join(allowed_types)}"
            )

        return value

    def validate_filename(self, value: str) -> str:
        """Validate filename."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Filename cannot be empty")

        
        dangerous_chars = ['..', '/', '\\', '\x00']
        for char in dangerous_chars:
            if char in value:
                raise serializers.ValidationError(
                    f"Filename contains invalid character: {char}"
                )

        return value


class PresignedUploadResponseSerializer(serializers.Serializer):
    """Response with presigned URL."""

    upload_url = serializers.URLField(
        help_text="S3 presigned upload URL"
    )
    upload_fields = serializers.DictField(
        help_text="Form fields to include in upload request"
    )
    s3_key = serializers.CharField(
        help_text="S3 object key (save this for later reference)"
    )
    expires_in = serializers.IntegerField(
        help_text="URL validity in seconds"
    )


class GeneratePresignedUploadURLView(APIView):
    """
    Generate presigned URL for direct browser upload to S3.

    Flow:
    1. Frontend calls this endpoint with filename + content_type
    2. Backend generates presigned URL + S3 key
    3. Frontend uploads file directly to S3 using presigned URL
    4. Frontend calls another endpoint with s3_key to finalize submission

    Security:
    - Authenticated users only
    - Max file size: 100MB (configurable)
    - Content type whitelist
    - Unique S3 keys per user/submission
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PresignedUploadRequestSerializer,
        responses={200: PresignedUploadResponseSerializer},
        tags=['Submissions — Uploads'],
        description=(
            "Generate presigned URL for direct S3 upload. "
            "Use this URL to upload file from browser without going through backend."
        ),
    )
    def post(self, request) -> Response:
        """Generate presigned upload URL."""
        serializer = PresignedUploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        filename = serializer.validated_data['filename']
        content_type = serializer.validated_data['content_type']
        submission_id = serializer.validated_data['submission_id']

        
        
        user_id = str(request.user.id)
        file_uuid = str(uuid.uuid4())

        
        name, ext = os.path.splitext(filename)
        safe_filename = f"{file_uuid}_{name[:50]}{ext}"  

        s3_key = f"submissions/{user_id}/{submission_id}/{safe_filename}"

        
        s3_client = get_s3_client()

        presigned_data = s3_client.generate_presigned_upload_url(
            key=s3_key,
            content_type=content_type,
            expires_in=3600,  
            max_size_mb=100,
            metadata={
                'user_id': user_id,
                'submission_id': str(submission_id),
                'original_filename': filename,
            }
        )

        return Response({
            'upload_url': presigned_data['url'],
            'upload_fields': presigned_data['fields'],
            's3_key': s3_key,
            'expires_in': 3600,
        }, status=status.HTTP_200_OK)
