"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentUploadResponse(BaseModel):
    """Response after successful document upload"""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    s3_key: str = Field(..., description="S3 object key")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    status: DocumentStatus = Field(default=DocumentStatus.UPLOADED)


class ProcessingRequest(BaseModel):
    """Request to process a document"""
    prompt_version: Optional[str] = Field(None, description="Prompt version to use")


class ProcessingResponse(BaseModel):
    """Response after initiating processing"""
    document_id: str
    status: DocumentStatus
    message: str


class MedicalData(BaseModel):
    """Extracted medical data structure"""
    patient_name: Optional[str] = Field(None, description="Patient full name")
    date_of_birth: Optional[str] = Field(None, description="Patient DOB")
    diagnoses: List[str] = Field(default_factory=list, description="List of diagnoses")
    medications: List[str] = Field(default_factory=list, description="List of medications")
    lab_values: Dict[str, Any] = Field(default_factory=dict, description="Lab test results")
    procedures: List[str] = Field(default_factory=list, description="Medical procedures")
    allergies: List[str] = Field(default_factory=list, description="Known allergies")
    vital_signs: Dict[str, Any] = Field(default_factory=dict, description="Vital signs")
    notes: Optional[str] = Field(None, description="Additional notes")


class ExtractionResult(BaseModel):
    """Complete extraction result with metadata"""
    document_id: str
    filename: str
    status: DocumentStatus
    medical_data: Optional[MedicalData] = None
    extracted_at: Optional[datetime] = None
    processing_time_ms: Optional[int] = None
    model_id: Optional[str] = None
    prompt_version: Optional[str] = None
    token_usage: Optional[Dict[str, int]] = None
    error_message: Optional[str] = None


class DocumentListItem(BaseModel):
    """Document list item for GET /documents"""
    document_id: str
    filename: str
    status: DocumentStatus
    uploaded_at: datetime
    extracted_at: Optional[datetime] = None
