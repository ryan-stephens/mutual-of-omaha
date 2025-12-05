"""
Upload endpoint for document submission
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import DocumentUploadResponse, DocumentStatus
from app.services import S3Service, DynamoDBService
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

s3_service = S3Service()
dynamodb_service = DynamoDBService()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a medical document
    
    Args:
        file: Uploaded file (PDF, TXT, DOC, DOCX)
        
    Returns:
        DocumentUploadResponse with document ID and metadata
    """
    try:
        allowed_extensions = ['.pdf', '.txt', '.doc', '.docx']
        file_ext = '.' + file.filename.split('.')[-1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        max_size_mb = 10
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {max_size_mb}MB"
            )
        
        logger.info(f"Uploading file: {file.filename} ({file_size_mb:.2f}MB)")
        
        document_id, s3_key = s3_service.upload_file(content, file.filename)
        
        success = dynamodb_service.save_document_metadata(
            document_id=document_id,
            filename=file.filename,
            s3_key=s3_key,
            status=DocumentStatus.UPLOADED
        )
        
        if not success:
            logger.warning(f"Failed to save metadata for {document_id}")
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            s3_key=s3_key,
            uploaded_at=datetime.utcnow(),
            status=DocumentStatus.UPLOADED
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/documents")
async def list_documents():
    """
    List all uploaded documents
    
    Returns:
        List of documents with metadata
    """
    try:
        documents = dynamodb_service.list_documents()
        return {"documents": documents, "count": len(documents)}
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")
