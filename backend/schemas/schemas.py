"""
CaseSync Pydantic Schemas
Request and response schemas for API validation and serialization.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


# ============== Enums ==============

class LanguageEnum(str, Enum):
    """Supported languages."""
    HINDI = "hi"
    ENGLISH = "en"


class CaseStatusEnum(str, Enum):
    """Case status lifecycle."""
    DRAFT = "DRAFT"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# ============== Case Schemas ==============

class CaseBase(BaseModel):
    """Base schema for case data."""
    language: LanguageEnum = LanguageEnum.ENGLISH


class CaseCreate(CaseBase):
    """Schema for creating a new case."""
    pass


class CaseResponse(CaseBase):
    """Schema for case response with all fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    status: CaseStatusEnum
    created_at: datetime
    updated_at: datetime


class CaseListResponse(BaseModel):
    """Schema for listing multiple cases."""
    cases: List[CaseResponse]
    total: int


# ============== Transcript Schemas ==============

class TranscriptBase(BaseModel):
    """Base schema for transcript data."""
    text: str = Field(..., min_length=1, description="Transcribed text content")


class TranscriptCreate(TranscriptBase):
    """Schema for creating a transcript."""
    case_id: UUID
    audio_filename: Optional[str] = None
    duration_seconds: Optional[str] = None


class TranscriptResponse(TranscriptBase):
    """Schema for transcript response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    case_id: UUID
    audio_filename: Optional[str] = None
    duration_seconds: Optional[str] = None
    created_at: datetime


class TranscriptUpdate(BaseModel):
    """Schema for updating transcript text."""
    text: str = Field(..., min_length=1)


# ============== Entity Schemas ==============

class EntityBase(BaseModel):
    """Base schema for extracted entities."""
    person_names: List[str] = Field(default_factory=list, description="Extracted person names")
    locations: List[str] = Field(default_factory=list, description="Extracted locations")
    dates: List[str] = Field(default_factory=list, description="Extracted dates/times")
    incident: Optional[str] = Field(None, description="Incident description")


class EntityCreate(EntityBase):
    """Schema for creating entity record."""
    case_id: UUID
    raw_entities: Optional[Any] = None


class EntityResponse(EntityBase):
    """Schema for entity response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    case_id: UUID
    raw_entities: Optional[Any] = None
    created_at: datetime
    updated_at: datetime


class EntityUpdate(BaseModel):
    """Schema for updating entities (officer corrections)."""
    person_names: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    dates: Optional[List[str]] = None
    incident: Optional[str] = None


# ============== FIR Draft Schemas ==============

class FIRDraftBase(BaseModel):
    """Base schema for FIR draft."""
    content: str = Field(..., min_length=1, description="FIR draft content")


class FIRDraftCreate(FIRDraftBase):
    """Schema for creating FIR draft."""
    case_id: UUID


class FIRDraftResponse(FIRDraftBase):
    """Schema for FIR draft response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    case_id: UUID
    status: CaseStatusEnum
    officer_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    approved_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FIRDraftUpdate(BaseModel):
    """Schema for updating FIR draft content."""
    content: str = Field(..., min_length=1)
    officer_notes: Optional[str] = None


# ============== Audio Upload Schemas ==============

class AudioUploadResponse(BaseModel):
    """Response schema for audio upload endpoint."""
    success: bool = True
    message: str
    case_id: UUID
    transcript: str
    detected_language: LanguageEnum
    audio_filename: str


# ============== NER Extraction Schemas ==============

class NERExtractionRequest(BaseModel):
    """Request schema for NER extraction (if manual trigger needed)."""
    text: Optional[str] = None  # If provided, use this instead of stored transcript


class NERExtractionResponse(BaseModel):
    """Response schema for NER extraction."""
    success: bool = True
    case_id: UUID
    entities: EntityResponse


# ============== FIR Generation Schemas ==============

class FIRGenerateRequest(BaseModel):
    """Request schema for FIR generation."""
    # Optional overrides for entity data
    complainant_name: Optional[str] = None
    complainant_address: Optional[str] = None
    police_station: Optional[str] = Field(default="Central Police Station")


class FIRGenerateResponse(BaseModel):
    """Response schema for FIR generation."""
    success: bool = True
    case_id: UUID
    fir_content: str
    language: LanguageEnum
    status: CaseStatusEnum


# ============== Review Schemas ==============

class ReviewStatusUpdate(BaseModel):
    """Schema for updating case/FIR status."""
    status: CaseStatusEnum
    officer_name: Optional[str] = None
    notes: Optional[str] = None


class ReviewResponse(BaseModel):
    """Response schema for review operations."""
    success: bool = True
    case_id: UUID
    previous_status: CaseStatusEnum
    new_status: CaseStatusEnum
    updated_at: datetime
    message: str


# ============== PDF Schemas ==============

class PDFGenerateResponse(BaseModel):
    """Response schema for PDF generation."""
    success: bool = True
    case_id: UUID
    filename: str
    message: str


# ============== Dashboard/List Schemas ==============

class CaseDetailResponse(BaseModel):
    """Complete case details for dashboard."""
    case: CaseResponse
    transcript: Optional[TranscriptResponse] = None
    entities: Optional[EntityResponse] = None
    fir_draft: Optional[FIRDraftResponse] = None


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_cases: int
    draft_cases: int
    reviewed_cases: int
    approved_cases: int
    rejected_cases: int
    hindi_cases: int
    english_cases: int


# ============== Generic Response Schemas ==============

class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    """Generic error response."""
    success: bool = False
    message: str
    detail: Optional[str] = None
