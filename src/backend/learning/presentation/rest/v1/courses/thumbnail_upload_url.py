from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import boto3
from botocore.exceptions import ClientError
import uuid
from src.backend.learning.utils.permissions import IsAdminOrStaff


class CourseThumbnailUploadUrlView(APIView):
    """Получить presigned URL для загрузки thumbnail курса"""
    permission_classes = [IsAdminOrStaff]

    def post(self, request):
        filename = request.data.get('filename')
        content_type = request.data.get('content_type', 'image/jpeg')

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

        
        ext = filename.split('.')[-1] if '.' in filename else 'jpg'
        s3_key = f"course-thumbnails/{uuid.uuid4()}.{ext}"

        
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


class CourseThumbnailUrlView(APIView):
    """Получить публичный URL для thumbnail курса"""
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
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