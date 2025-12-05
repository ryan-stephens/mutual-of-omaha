"""
S3 service for document storage
"""

import boto3
from botocore.exceptions import ClientError
from app.config import settings
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class S3Service:
    """Service for interacting with AWS S3"""

    def __init__(self):
        self.s3_client = boto3.client("s3", region_name=settings.AWS_REGION)
        self.bucket_name = settings.S3_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create S3 bucket if it doesn't exist"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"S3 bucket '{self.bucket_name}' exists")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                logger.info(f"Creating S3 bucket: {self.bucket_name}")
                try:
                    if settings.AWS_REGION == "us-east-1":
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={
                                "LocationConstraint": settings.AWS_REGION
                            },
                        )

                    self.s3_client.put_bucket_versioning(
                        Bucket=self.bucket_name,
                        VersioningConfiguration={"Status": "Enabled"},
                    )
                    logger.info(f"Successfully created bucket: {self.bucket_name}")
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    raise
            else:
                logger.error(f"Error checking bucket: {e}")
                raise

    def upload_file(self, file_content: bytes, filename: str) -> tuple[str, str]:
        """
        Upload file to S3

        Args:
            file_content: File bytes
            filename: Original filename

        Returns:
            Tuple of (document_id, s3_key)
        """
        document_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        s3_key = f"documents/{timestamp}-{document_id}/{filename}"

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=self._get_content_type(filename),
                Metadata={
                    "document-id": document_id,
                    "original-filename": filename,
                    "upload-timestamp": timestamp,
                },
            )
            logger.info(f"Uploaded file to S3: {s3_key}")
            return document_id, s3_key

        except ClientError as e:
            logger.error(f"Failed to upload to S3: {e}")
            raise

    def download_file(self, s3_key: str) -> bytes:
        """
        Download file from S3

        Args:
            s3_key: S3 object key

        Returns:
            File content as bytes
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response["Body"].read()

        except ClientError as e:
            logger.error(f"Failed to download from S3: {e}")
            raise

    def delete_file(self, s3_key: str) -> bool:
        """
        Delete file from S3

        Args:
            s3_key: S3 object key

        Returns:
            True if successful
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"Deleted file from S3: {s3_key}")
            return True

        except ClientError as e:
            logger.error(f"Failed to delete from S3: {e}")
            return False

    def list_files(self, prefix: str = "documents/") -> list:
        """
        List files in S3 bucket

        Args:
            prefix: S3 key prefix to filter

        Returns:
            List of S3 object summaries
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix
            )
            return response.get("Contents", [])

        except ClientError as e:
            logger.error(f"Failed to list S3 files: {e}")
            return []

    @staticmethod
    def _get_content_type(filename: str) -> str:
        """Get content type based on file extension"""
        extension = filename.lower().split(".")[-1]
        content_types = {
            "pdf": "application/pdf",
            "txt": "text/plain",
            "doc": "application/msword",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
        }
        return content_types.get(extension, "application/octet-stream")
