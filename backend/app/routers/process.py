"""
Processing endpoint for medical data extraction
"""

import io
import logging
from datetime import datetime
from typing import Optional

import PyPDF2
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    DocumentStatus,
    ExtractionResult,
    ProcessingRequest,
)
from app.services import BedrockService, DynamoDBService, S3Service

router = APIRouter()
logger = logging.getLogger(__name__)

s3_service = S3Service()
dynamodb_service = DynamoDBService()
bedrock_service = BedrockService()


@router.post("/process/{document_id}", response_model=ExtractionResult)
async def process_document(document_id: str, request: Optional[ProcessingRequest] = None):
    """
    Process a document and extract medical data using Bedrock

    Args:
        document_id: Document identifier
        request: Optional processing parameters

    Returns:
        ExtractionResult with extracted medical data
    """
    try:
        metadata = dynamodb_service.get_result(document_id)

        if not metadata:
            raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")

        dynamodb_service.update_status(document_id, DocumentStatus.PROCESSING)

        logger.info(f"Processing document: {document_id}")

        file_content = s3_service.download_file(metadata["s3_key"])

        document_text = _extract_text_from_file(file_content, metadata["filename"])

        if not document_text or len(document_text.strip()) < 10:
            dynamodb_service.update_status(document_id, DocumentStatus.FAILED)
            raise HTTPException(status_code=400, detail="Could not extract text from document")

        prompt_version = request.prompt_version if request else "v1"

        (
            medical_data,
            token_usage,
            processing_time,
        ) = bedrock_service.extract_medical_data(document_text, prompt_version=prompt_version)

        if not medical_data:
            dynamodb_service.update_status(document_id, DocumentStatus.FAILED)
            raise HTTPException(status_code=500, detail="Failed to parse extraction results")

        result = ExtractionResult(
            document_id=document_id,
            filename=metadata["filename"],
            status=DocumentStatus.COMPLETED,
            medical_data=medical_data,
            extracted_at=datetime.utcnow(),
            processing_time_ms=processing_time,
            model_id=bedrock_service.model_id,
            prompt_version=prompt_version,
            token_usage=token_usage,
        )

        dynamodb_service.save_extraction_result(result)

        logger.info(f"Successfully processed document: {document_id}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing failed for {document_id}: {e}")
        dynamodb_service.update_status(document_id, DocumentStatus.FAILED)

        result = ExtractionResult(
            document_id=document_id,
            filename=metadata.get("filename", "unknown") if metadata else "unknown",
            status=DocumentStatus.FAILED,
            error_message=str(e),
        )
        dynamodb_service.save_extraction_result(result)

        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


def _extract_text_from_file(file_content: bytes, filename: str) -> str:
    """
    Extract text from various file formats

    Args:
        file_content: File bytes
        filename: Original filename

    Returns:
        Extracted text content
    """
    file_ext = filename.lower().split(".")[-1]

    try:
        if file_ext == "pdf":
            return _extract_text_from_pdf(file_content)
        elif file_ext == "txt":
            return file_content.decode("utf-8")
        elif file_ext in ["doc", "docx"]:
            return "Document format not yet supported. Please convert to PDF or TXT."
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        raise


def _extract_text_from_pdf(pdf_content: bytes) -> str:
    """
    Extract text from PDF file

    Args:
        pdf_content: PDF file bytes

    Returns:
        Extracted text
    """
    try:
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        text_parts = []
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

        full_text = "\n\n".join(text_parts)

        logger.info(f"Extracted {len(full_text)} characters from PDF")

        return full_text

    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise ValueError(f"Could not extract text from PDF: {e}")
