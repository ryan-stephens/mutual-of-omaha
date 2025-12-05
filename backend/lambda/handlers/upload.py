"""
Lambda handler for document upload operations
"""

import logging
import base64
from datetime import datetime
import sys
import os

sys.path.insert(0, "/opt/python")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
# Add parent directory to path to import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import create_response, create_error_response, parse_event_body
from app.models.schemas import DocumentStatus
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize AWS clients directly (avoid S3Service bucket check)
s3_client = boto3.client("s3")
dynamodb_client = boto3.client("dynamodb")
dynamodb_resource = boto3.resource("dynamodb")

# Get environment variables
S3_BUCKET = os.environ.get("S3_BUCKET")
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE")


def handler(event, context):
    """
    Process document upload requests

    Expects multipart/form-data with base64 encoded file
    """
    try:
        logger.info(
            f"Upload request received: {event.get('requestContext', {}).get('requestId')}"
        )

        body = parse_event_body(event)

        if not body.get("file_content") or not body.get("filename"):
            return create_error_response(
                400, "Missing required fields: file_content and filename"
            )

        filename = body["filename"]
        file_content_b64 = body["file_content"]

        allowed_extensions = [".pdf", ".txt", ".doc", ".docx"]
        file_ext = "." + filename.split(".")[-1].lower()

        if file_ext not in allowed_extensions:
            return create_error_response(
                400,
                f"File type not supported. Allowed: {', '.join(allowed_extensions)}",
            )

        try:
            file_content = base64.b64decode(file_content_b64)
        except Exception as e:
            logger.error(f"Failed to decode base64: {e}")
            return create_error_response(400, "Invalid base64 encoded file")

        file_size_mb = len(file_content) / (1024 * 1024)
        max_size_mb = 10

        if file_size_mb > max_size_mb:
            return create_error_response(
                413, f"File too large. Maximum size: {max_size_mb}MB"
            )

        logger.info(f"Uploading file: {filename} ({file_size_mb:.2f}MB)")

        # Generate document ID and S3 key
        import uuid
        document_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        s3_key = f"documents/{timestamp}_{document_id}_{filename}"

        # Upload to S3
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=file_content,
            ContentType="application/octet-stream",
        )
        logger.info(f"Uploaded to S3: {s3_key}")

        # Save metadata to DynamoDB
        table = dynamodb_resource.Table(DYNAMODB_TABLE)
        table.put_item(
            Item={
                "document_id": document_id,
                "filename": filename,
                "s3_key": s3_key,
                "status": DocumentStatus.UPLOADED.value,
                "uploaded_at": datetime.utcnow().isoformat(),
                "file_size_bytes": len(file_content),
            }
        )
        logger.info(f"Saved metadata to DynamoDB: {document_id}")

        return create_response(
            200,
            {
                "document_id": document_id,
                "filename": filename,
                "s3_key": s3_key,
                "uploaded_at": datetime.utcnow().isoformat(),
                "status": DocumentStatus.UPLOADED.value,
            },
        )

    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        return create_error_response(500, f"Upload failed: {str(e)}")
