"""
DynamoDB service for storing extraction results
"""

import boto3
from botocore.exceptions import ClientError
from app.config import settings
from app.models.schemas import ExtractionResult, DocumentStatus
import logging
from typing import Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class DynamoDBService:
    """Service for interacting with DynamoDB"""
    
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=settings.AWS_REGION
        )
        self.table_name = settings.DYNAMODB_TABLE_NAME
        self.table = None
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Create DynamoDB table if it doesn't exist"""
        try:
            self.table = self.dynamodb.Table(self.table_name)
            self.table.load()
            logger.info(f"DynamoDB table '{self.table_name}' exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                logger.info(f"Creating DynamoDB table: {self.table_name}")
                self._create_table()
            else:
                logger.error(f"Error checking table: {e}")
                raise
    
    def _create_table(self):
        """Create the DynamoDB table with proper schema"""
        try:
            self.table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {'AttributeName': 'document_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'document_id', 'AttributeType': 'S'},
                    {'AttributeName': 'uploaded_at', 'AttributeType': 'S'}
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'UploadedAtIndex',
                        'KeySchema': [
                            {'AttributeName': 'uploaded_at', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'},
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            
            self.table.wait_until_exists()
            logger.info(f"Successfully created table: {self.table_name}")
            
        except ClientError as e:
            logger.error(f"Failed to create table: {e}")
            raise
    
    def save_document_metadata(
        self,
        document_id: str,
        filename: str,
        s3_key: str,
        status: DocumentStatus = DocumentStatus.UPLOADED
    ) -> bool:
        """
        Save initial document metadata
        
        Args:
            document_id: Unique document identifier
            filename: Original filename
            s3_key: S3 object key
            status: Document status
            
        Returns:
            True if successful
        """
        try:
            timestamp = datetime.utcnow().isoformat()
            
            self.table.put_item(
                Item={
                    'document_id': document_id,
                    'filename': filename,
                    's3_key': s3_key,
                    'status': status.value,
                    'uploaded_at': timestamp,
                    'updated_at': timestamp
                }
            )
            logger.info(f"Saved document metadata: {document_id}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to save metadata: {e}")
            return False
    
    def save_extraction_result(self, result: ExtractionResult) -> bool:
        """
        Save extraction result
        
        Args:
            result: ExtractionResult object
            
        Returns:
            True if successful
        """
        try:
            timestamp = datetime.utcnow().isoformat()
            
            item = {
                'document_id': result.document_id,
                'filename': result.filename,
                'status': result.status.value,
                'updated_at': timestamp
            }
            
            if result.medical_data:
                item['medical_data'] = json.loads(result.medical_data.model_dump_json())
            
            if result.extracted_at:
                item['extracted_at'] = result.extracted_at.isoformat()
            
            if result.processing_time_ms:
                item['processing_time_ms'] = result.processing_time_ms
            
            if result.model_id:
                item['model_id'] = result.model_id
            
            if result.prompt_version:
                item['prompt_version'] = result.prompt_version
            
            if result.token_usage:
                item['token_usage'] = result.token_usage
            
            if result.error_message:
                item['error_message'] = result.error_message
            
            self.table.put_item(Item=item)
            logger.info(f"Saved extraction result: {result.document_id}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to save extraction result: {e}")
            return False
    
    def get_result(self, document_id: str) -> Optional[dict]:
        """
        Get extraction result by document ID
        
        Args:
            document_id: Document identifier
            
        Returns:
            Result dict or None
        """
        try:
            response = self.table.get_item(
                Key={'document_id': document_id}
            )
            return response.get('Item')
            
        except ClientError as e:
            logger.error(f"Failed to get result: {e}")
            return None
    
    def list_documents(self, limit: int = 50) -> List[dict]:
        """
        List all documents
        
        Args:
            limit: Maximum number of documents to return
            
        Returns:
            List of document items
        """
        try:
            response = self.table.scan(Limit=limit)
            items = response.get('Items', [])
            
            items.sort(key=lambda x: x.get('uploaded_at', ''), reverse=True)
            return items
            
        except ClientError as e:
            logger.error(f"Failed to list documents: {e}")
            return []
    
    def update_status(self, document_id: str, status: DocumentStatus) -> bool:
        """
        Update document processing status
        
        Args:
            document_id: Document identifier
            status: New status
            
        Returns:
            True if successful
        """
        try:
            timestamp = datetime.utcnow().isoformat()
            
            self.table.update_item(
                Key={'document_id': document_id},
                UpdateExpression='SET #status = :status, updated_at = :timestamp',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': status.value,
                    ':timestamp': timestamp
                }
            )
            logger.info(f"Updated status for {document_id}: {status.value}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to update status: {e}")
            return False
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete document from DynamoDB
        
        Args:
            document_id: Document identifier
            
        Returns:
            True if successful
        """
        try:
            self.table.delete_item(
                Key={'document_id': document_id}
            )
            logger.info(f"Deleted document: {document_id}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete document: {e}")
            return False
