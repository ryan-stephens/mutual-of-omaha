"""
Results endpoint for retrieving extraction results
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import ExtractionResult, DocumentStatus, MedicalData
from app.services import DynamoDBService
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

dynamodb_service = DynamoDBService()


@router.get("/results/{document_id}", response_model=ExtractionResult)
async def get_results(document_id: str):
    """
    Get extraction results for a document

    Args:
        document_id: Document identifier

    Returns:
        ExtractionResult with medical data
    """
    try:
        result = dynamodb_service.get_result(document_id)

        if not result:
            raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")

        medical_data = None
        if "medical_data" in result and result["medical_data"]:
            medical_data = MedicalData(**result["medical_data"])

        extracted_at = None
        if "extracted_at" in result:
            extracted_at = datetime.fromisoformat(result["extracted_at"])

        return ExtractionResult(
            document_id=result["document_id"],
            filename=result.get("filename", "unknown"),
            status=DocumentStatus(result.get("status", "uploaded")),
            medical_data=medical_data,
            extracted_at=extracted_at,
            processing_time_ms=result.get("processing_time_ms"),
            model_id=result.get("model_id"),
            prompt_version=result.get("prompt_version"),
            token_usage=result.get("token_usage"),
            error_message=result.get("error_message"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get results for {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")


@router.delete("/results/{document_id}")
async def delete_results(document_id: str):
    """
    Delete a document and its results

    Args:
        document_id: Document identifier

    Returns:
        Success message
    """
    try:
        result = dynamodb_service.get_result(document_id)

        if not result:
            raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")

        success = dynamodb_service.delete_document(document_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete document")

        return {"message": "Document deleted successfully", "document_id": document_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
