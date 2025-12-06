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


class Diagnosis(BaseModel):
    """Structured diagnosis information"""

    condition: str = Field(..., description="Diagnosis name")
    icd_code: Optional[str] = Field(None, description="ICD-10 code")
    severity: Optional[str] = Field(None, description="Severity level")
    date_diagnosed: Optional[str] = Field(None, description="Date diagnosed")


class Medication(BaseModel):
    """Structured medication information"""

    name: str = Field(..., description="Medication name")
    dosage: Optional[str] = Field(None, description="Dosage and strength")
    frequency: Optional[str] = Field(None, description="Frequency")
    route: Optional[str] = Field(None, description="Administration route")
    indication: Optional[str] = Field(None, description="Reason for medication")


class LabValue(BaseModel):
    """Structured lab value information"""

    value: str = Field(..., description="Test result with units")
    reference_range: Optional[str] = Field(None, description="Normal range")
    date: Optional[str] = Field(None, description="Test date")
    flag: Optional[str] = Field(None, description="H/L/Normal flag")


class Procedure(BaseModel):
    """Structured procedure information"""

    name: str = Field(..., description="Procedure name")
    date: Optional[str] = Field(None, description="Date performed")
    outcome: Optional[str] = Field(None, description="Result or status")


class Allergy(BaseModel):
    """Structured allergy information"""

    allergen: str = Field(..., description="Allergen name")
    reaction: Optional[str] = Field(None, description="Type of reaction")
    severity: Optional[str] = Field(None, description="Severity level")


class VitalSign(BaseModel):
    """Structured vital sign information"""

    value: str = Field(..., description="Measurement with units")
    date: Optional[str] = Field(None, description="When measured")


class MedicalData(BaseModel):
    """Extracted medical data structure - supports both simple and structured formats"""

    patient_name: Optional[str] = Field(None, description="Patient full name")
    date_of_birth: Optional[str] = Field(None, description="Patient DOB")
    diagnoses: List[Diagnosis | str] = Field(default_factory=list, description="List of diagnoses")
    medications: List[Medication | str] = Field(
        default_factory=list, description="List of medications"
    )
    lab_values: Dict[str, LabValue | str | Any] = Field(
        default_factory=dict, description="Lab test results"
    )
    procedures: List[Procedure | str] = Field(
        default_factory=list, description="Medical procedures"
    )
    allergies: List[Allergy | str] = Field(default_factory=list, description="Known allergies")
    vital_signs: Dict[str, VitalSign | str | Any] = Field(
        default_factory=dict, description="Vital signs"
    )
    risk_factors: List[str] = Field(
        default_factory=list, description="Risk factors for underwriting"
    )
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
