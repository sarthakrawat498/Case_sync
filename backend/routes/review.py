"""
Officer Review Routes
Handles FIR review workflow: Edit, Review, Approve.
"""

from uuid import UUID
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database import get_db
from models.models import Case, FIRDraft, CaseStatusEnum, Entity, Transcript
from schemas.schemas import (
    ReviewStatusUpdate, ReviewResponse, CaseResponse, CaseListResponse,
    CaseDetailResponse, FIRDraftResponse, EntityResponse, TranscriptResponse,
    DashboardStats
)


router = APIRouter()


@router.put("/status/{case_id}", response_model=ReviewResponse)
async def update_case_status(
    case_id: str,
    status_update: ReviewStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Update case and FIR status.
    
    Status lifecycle: DRAFT → REVIEWED → APPROVED
    
    Args:
        case_id: UUID of the case
        status_update: New status and optional officer info
        
    Returns:
        Status update confirmation
    """
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    # Get case
    case = db.query(Case).filter(Case.id == case_uuid).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get FIR draft
    fir_draft = db.query(FIRDraft).filter(FIRDraft.case_id == case_uuid).first()
    if not fir_draft:
        raise HTTPException(
            status_code=404,
            detail="FIR draft not found. Please generate FIR first."
        )
    
    # Store previous status
    previous_status = case.status
    new_status = status_update.status
    
    # Validate status transitions
    valid_transitions = {
        CaseStatusEnum.DRAFT: [CaseStatusEnum.REVIEWED],
        CaseStatusEnum.REVIEWED: [CaseStatusEnum.DRAFT, CaseStatusEnum.APPROVED, CaseStatusEnum.REJECTED],
        CaseStatusEnum.APPROVED: [],  # No transitions from APPROVED
        CaseStatusEnum.REJECTED: [CaseStatusEnum.DRAFT]  # Can return rejected to draft for corrections
    }
    
    if new_status not in valid_transitions.get(previous_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from {previous_status.value} to {new_status.value}"
        )
    
    # Update case status
    case.status = new_status
    
    # Update FIR draft status and officer info
    fir_draft.status = new_status
    
    if status_update.officer_name:
        if new_status == CaseStatusEnum.REVIEWED:
            fir_draft.reviewed_by = status_update.officer_name
        elif new_status == CaseStatusEnum.APPROVED:
            fir_draft.approved_by = status_update.officer_name
    
    if status_update.notes:
        fir_draft.officer_notes = status_update.notes
    
    db.commit()
    db.refresh(case)
    db.refresh(fir_draft)
    
    # Create response message
    status_messages = {
        CaseStatusEnum.REVIEWED: "FIR has been marked as reviewed",
        CaseStatusEnum.APPROVED: "FIR has been approved and finalized",
        CaseStatusEnum.REJECTED: "FIR has been rejected and requires corrections",
        CaseStatusEnum.DRAFT: "FIR has been returned to draft status"
    }
    
    return ReviewResponse(
        success=True,
        case_id=case_uuid,
        previous_status=previous_status,
        new_status=new_status,
        updated_at=fir_draft.updated_at,
        message=status_messages.get(new_status, "Status updated")
    )


@router.put("/edit/{case_id}", response_model=FIRDraftResponse)
async def edit_fir_content(
    case_id: str,
    content: str,
    officer_notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Edit FIR content directly.
    Only allowed for DRAFT and REVIEWED status.
    
    Args:
        case_id: UUID of the case
        content: New FIR content
        officer_notes: Optional notes about the edit
        
    Returns:
        Updated FIR draft
    """
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    # Get FIR draft
    fir_draft = db.query(FIRDraft).filter(FIRDraft.case_id == case_uuid).first()
    
    if not fir_draft:
        raise HTTPException(status_code=404, detail="FIR draft not found")
    
    # Check if editing is allowed
    if fir_draft.status == CaseStatusEnum.APPROVED:
        raise HTTPException(
            status_code=400,
            detail="Cannot edit an approved FIR"
        )
    
    # Update content
    fir_draft.content = content
    
    if officer_notes:
        existing_notes = fir_draft.officer_notes or ""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        fir_draft.officer_notes = f"{existing_notes}\n[{timestamp}] {officer_notes}".strip()
    
    db.commit()
    db.refresh(fir_draft)
    
    return fir_draft


@router.get("/cases", response_model=CaseListResponse)
async def list_cases(
    status: Optional[CaseStatusEnum] = None,
    language: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List all cases with optional filtering.
    
    Args:
        status: Filter by case status
        language: Filter by language (hi/en)
        skip: Pagination offset
        limit: Number of results
        
    Returns:
        List of cases with total count
    """
    from models.models import LanguageEnum
    
    query = db.query(Case)
    
    # Apply filters
    if status:
        query = query.filter(Case.status == status)
    
    if language:
        if language.lower() in ['hi', 'hindi']:
            query = query.filter(Case.language == LanguageEnum.HINDI)
        elif language.lower() in ['en', 'english']:
            query = query.filter(Case.language == LanguageEnum.ENGLISH)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    cases = query.order_by(desc(Case.created_at)).offset(skip).limit(limit).all()
    
    return CaseListResponse(
        cases=[CaseResponse.model_validate(c) for c in cases],
        total=total
    )


@router.get("/case/{case_id}", response_model=CaseDetailResponse)
async def get_case_detail(
    case_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete case details including transcript, entities, and FIR draft.
    
    Args:
        case_id: UUID of the case
        
    Returns:
        Complete case information
    """
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    # Get case
    case = db.query(Case).filter(Case.id == case_uuid).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get related data
    transcript = db.query(Transcript).filter(Transcript.case_id == case_uuid).first()
    entity = db.query(Entity).filter(Entity.case_id == case_uuid).first()
    fir_draft = db.query(FIRDraft).filter(FIRDraft.case_id == case_uuid).first()
    
    return CaseDetailResponse(
        case=CaseResponse.model_validate(case),
        transcript=TranscriptResponse.model_validate(transcript) if transcript else None,
        entities=EntityResponse.model_validate(entity) if entity else None,
        fir_draft=FIRDraftResponse.model_validate(fir_draft) if fir_draft else None
    )


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics.
    
    Returns:
        Case counts by status and language
    """
    from models.models import LanguageEnum
    
    total = db.query(Case).count()
    draft = db.query(Case).filter(Case.status == CaseStatusEnum.DRAFT).count()
    reviewed = db.query(Case).filter(Case.status == CaseStatusEnum.REVIEWED).count()
    approved = db.query(Case).filter(Case.status == CaseStatusEnum.APPROVED).count()
    rejected = db.query(Case).filter(Case.status == CaseStatusEnum.REJECTED).count()
    hindi = db.query(Case).filter(Case.language == LanguageEnum.HINDI).count()
    english = db.query(Case).filter(Case.language == LanguageEnum.ENGLISH).count()
    
    return DashboardStats(
        total_cases=total,
        draft_cases=draft,
        reviewed_cases=reviewed,
        approved_cases=approved,
        rejected_cases=rejected,
        hindi_cases=hindi,
        english_cases=english
    )


@router.delete("/case/{case_id}")
async def delete_case(
    case_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a case and all its related data.
    Only allowed for DRAFT status cases.
    
    Args:
        case_id: UUID of the case to delete
        
    Returns:
        Success confirmation
    """
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    # Get case
    case = db.query(Case).filter(Case.id == case_uuid).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check if case can be deleted (only DRAFT cases)
    if case.status != CaseStatusEnum.DRAFT:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete case with status {case.status.value}. Only DRAFT cases can be deleted."
        )
    
    # Delete the case (cascade will handle related data)
    db.delete(case)
    db.commit()
    
    return {
        "success": True,
        "message": f"Case {case_id[:8]} and all related data deleted successfully"
    }
