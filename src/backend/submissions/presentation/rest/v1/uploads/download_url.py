"""
GET /api/v1/submissions/uploads/download-url/{file_id}/

Generate presigned URL for downloading file from S3.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, serializers
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from src.backend.shared.infrastructure.storage import get_s3_client
from src.backend.submissions.domain.models.file import SubmissionFile


class DownloadURLResponseSerializer(serializers.Serializer):
    """Response with presigned download URL."""

    download_url = serializers.URLField(
        help_text="S3 presigned download URL"
    )
    filename = serializers.CharField(
        help_text="Original filename"
    )
    expires_in = serializers.IntegerField(
        help_text="URL validity in seconds"
    )


class GeneratePresignedDownloadURLView(APIView):
    """
    Generate presigned URL for downloading file from S3.

    Security:
    - Authenticated users only
    - Only file owner or mentor can download
    - URLs expire after 1 hour
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: DownloadURLResponseSerializer},
        tags=['Submissions — Uploads'],
        description="Generate presigned URL for downloading file from S3.",
    )
    def get(self, request, file_id: str) -> Response:
        """Generate presigned download URL."""
        file_obj = get_object_or_404(SubmissionFile, id=file_id)

        
        submission = file_obj.submission
        user = request.user

        is_owner = submission.student_id == user.id
        is_mentor = user.role in ['mentor', 'staff', 'admin']

        if not (is_owner or is_mentor):
            return Response(
                {'detail': 'You do not have permission to download this file.'},
                status=status.HTTP_403_FORBIDDEN
            )

        
        s3_client = get_s3_client()

        download_url = s3_client.generate_presigned_download_url(
            key=file_obj.s3_key,
            expires_in=3600,  
            filename=file_obj.original_filename,
        )

        return Response({
            'download_url': download_url,
            'filename': file_obj.original_filename,
            'expires_in': 3600,
        }, status=status.HTTP_200_OK)
