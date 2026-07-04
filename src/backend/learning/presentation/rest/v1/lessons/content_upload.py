"""
Content Upload API — presigned URLs для загрузки файлов контента урока.

Endpoints:
- POST /api/v1/learning/lessons/{lesson_id}/content/upload-url/ — получить presigned URL
- GET  /api/v1/learning/lessons/content/url/ — получить публичный URL
"""

import uuid
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import get_object_or_404
import boto3
from botocore.exceptions import ClientError

from src.backend.learning.utils.permissions import IsAdminOrStaff
from src.backend.learning.domain.models import Lesson


class LessonContentUploadUrlView(APIView):
    """Получить presigned URL для загрузки файла контента урока."""
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request, lesson_id: str) -> Response:
        lesson = get_object_or_404(Lesson, id=lesson_id, deleted_at__isnull=True)

        filename = request.data.get('filename')
        content_type = request.data.get('content_type', 'application/octet-stream')

        if not filename:
            return Response(
                {'error': 'filename is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not settings.AWS_S3_ENDPOINT_URL:
            return Response(
                {'error': 'S3 storage is not configured'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        
        ext = filename.split('.')[-1] if '.' in filename else 'bin'
        s3_key = f"lesson-content/{lesson_id}/{uuid.uuid4()}.{ext}"

        s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        try:
            upload_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': s3_key,
                    'ContentType': content_type,
                },
                ExpiresIn=3600
            )

            return Response({
                'upload_url': upload_url,
                's3_key': s3_key,
            })
        except ClientError as e:
            return Response(
                {'error': f'Failed to generate upload URL: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LessonContentPublicUrlView(APIView):
    """Получить публичный URL для файла контента."""
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request: Request) -> Response:
        s3_key = request.query_params.get('s3_key')

        if not s3_key:
            return Response(
                {'error': 's3_key is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        endpoint = settings.AWS_S3_ENDPOINT_URL.rstrip('/')
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        public_url = f"{endpoint}/{bucket}/{s3_key}"

        return Response({'url': public_url})