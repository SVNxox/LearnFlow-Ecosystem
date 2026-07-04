"""
S3 Client — wrapper around boto3 for file operations.

Supports:
- Presigned URLs (upload/download)
- Direct upload/download
- File deletion
- Public/private access control

Compatible with: AWS S3, Cloudflare R2, MinIO
"""
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class S3Client:
    """
    Wrapper around boto3 S3 client.

    Usage:
        client = S3Client()

        
        upload_url = client.generate_presigned_upload_url(
            key="submissions/user123/file.pdf",
            content_type="application/pdf",
            max_size_mb=10
        )

        
        download_url = client.generate_presigned_download_url(
            key="submissions/user123/file.pdf",
            expires_in=3600
        )

        
        client.delete_file(key="submissions/user123/file.pdf")
    """

    def __init__(self):
        """Initialize boto3 S3 client from Django settings."""
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        
        config = Config(
            signature_version='s3v4',
            s3={'addressing_style': 'path'},  
        )

        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL or None,
            region_name=settings.AWS_S3_REGION_NAME,
            config=config,
        )

    def generate_presigned_upload_url(
        self,
        key: str,
        content_type: str,
        expires_in: int = 3600,
        max_size_mb: int = 100,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate presigned URL for direct browser upload to S3.

        Args:
            key: S3 object key (path in bucket)
            content_type: MIME type (e.g., "application/pdf")
            expires_in: URL validity in seconds (default 1 hour)
            max_size_mb: Max file size in MB (default 100)
            metadata: Custom metadata to attach to object

        Returns:
            {
                "url": "https://...",
                "fields": {"key": "...", "Content-Type": "...", ...}
            }

        Frontend usage:
            const formData = new FormData();
            Object.entries(response.fields).forEach(([k, v]) => {
                formData.append(k, v);
            });
            formData.append("file", file);

            await fetch(response.url, {
                method: "POST",
                body: formData
            });
        """
        try:
            conditions = [
                {"Content-Type": content_type},
                ["content-length-range", 0, max_size_mb * 1024 * 1024],
            ]

            fields = {
                "Content-Type": content_type,
            }

            if metadata:
                for k, v in metadata.items():
                    fields[f"x-amz-meta-{k}"] = v

            response = self.client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=key,
                Fields=fields,
                Conditions=conditions,
                ExpiresIn=expires_in,
            )

            logger.info(f"Generated presigned upload URL for key={key}")
            return response

        except ClientError as e:
            logger.error(f"Failed to generate presigned upload URL: {e}")
            raise

    def generate_presigned_download_url(
        self,
        key: str,
        expires_in: int = 3600,
        filename: Optional[str] = None,
    ) -> str:
        """
        Generate presigned URL for downloading file from S3.

        Args:
            key: S3 object key
            expires_in: URL validity in seconds (default 1 hour)
            filename: Optional filename for Content-Disposition header

        Returns:
            Presigned download URL
        """
        try:
            params = {
                'Bucket': self.bucket_name,
                'Key': key,
            }

            if filename:
                params['ResponseContentDisposition'] = f'attachment; filename="{filename}"'

            url = self.client.generate_presigned_url(
                ClientMethod='get_object',
                Params=params,
                ExpiresIn=expires_in,
            )

            logger.info(f"Generated presigned download URL for key={key}")
            return url

        except ClientError as e:
            logger.error(f"Failed to generate presigned download URL: {e}")
            raise

    def upload_file(
        self,
        file_obj,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Direct upload file to S3 (server-side).

        Args:
            file_obj: File-like object
            key: S3 object key
            content_type: MIME type
            metadata: Custom metadata

        Returns:
            S3 key
        """
        try:
            extra_args = {}

            if content_type:
                extra_args['ContentType'] = content_type

            if metadata:
                extra_args['Metadata'] = metadata

            self.client.upload_fileobj(
                Fileobj=file_obj,
                Bucket=self.bucket_name,
                Key=key,
                ExtraArgs=extra_args,
            )

            logger.info(f"Uploaded file to S3: key={key}")
            return key

        except ClientError as e:
            logger.error(f"Failed to upload file: {e}")
            raise

    def download_file(self, key: str) -> bytes:
        """
        Download file from S3 (server-side).

        Args:
            key: S3 object key

        Returns:
            File content as bytes
        """
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=key,
            )

            content = response['Body'].read()
            logger.info(f"Downloaded file from S3: key={key}")
            return content

        except ClientError as e:
            logger.error(f"Failed to download file: {e}")
            raise

    def delete_file(self, key: str) -> None:
        """
        Delete file from S3.

        Args:
            key: S3 object key
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=key,
            )

            logger.info(f"Deleted file from S3: key={key}")

        except ClientError as e:
            logger.error(f"Failed to delete file: {e}")
            raise

    def file_exists(self, key: str) -> bool:
        """
        Check if file exists in S3.

        Args:
            key: S3 object key

        Returns:
            True if file exists
        """
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            return True

        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise

    def get_file_metadata(self, key: str) -> Dict[str, Any]:
        """
        Get file metadata from S3.

        Args:
            key: S3 object key

        Returns:
            {
                "content_type": "application/pdf",
                "content_length": 12345,
                "last_modified": datetime,
                "metadata": {...}
            }
        """
        try:
            response = self.client.head_object(
                Bucket=self.bucket_name,
                Key=key,
            )

            return {
                "content_type": response.get('ContentType'),
                "content_length": response.get('ContentLength'),
                "last_modified": response.get('LastModified'),
                "metadata": response.get('Metadata', {}),
            }

        except ClientError as e:
            logger.error(f"Failed to get file metadata: {e}")
            raise



_s3_client: Optional[S3Client] = None


def get_s3_client() -> S3Client:
    """Get or create singleton S3Client instance."""
    global _s3_client

    if _s3_client is None:
        _s3_client = S3Client()

    return _s3_client
