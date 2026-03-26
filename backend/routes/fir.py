"""
FIR Generation Routes
Handles FIR draft generation from extracted entities.
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.models import Case, Entity, FIRDraft, CaseStatusEnum
from schemas.schemas import (
    FIRDraftResponse, FIRDraftUpdate, FIRGenerateRequest, FIRGenerateResponse
)
from services.fir_service import fir_service


router = APIRouter()


@router.post("/generate/{case_id}", response_model=FIRGenerateResponse)
async def generate_fir(
    case_id: str,
    request: FIRGenerateRequest = None,
    db: Session = Depends(get_db)
):
    """
    Generate FIR draft from extracted entities.
    
    Uses template-based generation (no LLM hallucination).
    Template adapts to detected language (Hindi/English).
    
    Args:
        case_id: UUID of the case
        request: Optional additional info (police station, etc.)
        
    Returns:
        Generated FIR draft content
    """
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    # Get case
    case = db.query(Case).filter(Case.id == case_uuid).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get entities
    entity = db.query(Entity).filter(Entity.case_id == case_uuid).first()
    if not entity:
        raise HTTPException(
            status_code=404,
            detail="Entities not found. Please run entity extraction first."
        )
    
    # Prepare entity data
    entities_data = {
        'person_names': entity.person_names or [],
        'locations': entity.locations or [],
        'dates': entity.dates or [],
        'incident': entity.incident or ''
    }
    
    # Prepare additional info from request
    additional_info = {}
    if request:
        if request.police_station:
            additional_info['police_station'] = request.police_station
        if request.complainant_name:
            entities_data['person_names'].insert(0, request.complainant_name)
        if request.complainant_address:
            additional_info['complainant_address'] = request.complainant_address
    
    # Generate FIR using template service
    try:
        fir_content = fir_service.generate_fir_draft(
            case_id=str(case_uuid),
            entities=entities_data,
            language=case.language.value,
            additional_info=additional_info
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"FIR generation failed: {str(e)}"
        )
    
    # Check if FIR draft already exists
    existing_fir = db.query(FIRDraft).filter(FIRDraft.case_id == case_uuid).first()
    
    if existing_fir:
        # Update existing FIR draft
        existing_fir.content = fir_content
        existing_fir.status = CaseStatusEnum.DRAFT
        db.commit()
        db.refresh(existing_fir)
        fir_draft = existing_fir
    else:
        # Create new FIR draft
        new_fir = FIRDraft(
            case_id=case_uuid,
            content=fir_content,
            status=CaseStatusEnum.DRAFT
        )
        db.add(new_fir)
        db.commit()
        db.refresh(new_fir)
        fir_draft = new_fir
    
    # Update case status to DRAFT
    case.status = CaseStatusEnum.DRAFT
    db.commit()
    
    return FIRGenerateResponse(
        success=True,
        case_id=case_uuid,
        fir_content=fir_content,
        language=case.language.value,
        status=CaseStatusEnum.DRAFT
    )


@router.get("/draft/{case_id}", response_model=FIRDraftResponse)
async def get_fir_draft(
    case_id: str,
    db: Session = Depends(get_db)
):
    """
    Get FIR draft for a case.
    
    Args:
        case_id: UUID of the case
        
    Returns:
        FIR draft content and metadata
    """
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    # Query FIR draft
    fir_draft = db.query(FIRDraft).filter(FIRDraft.case_id == case_uuid).first()
    
    if not fir_draft:
        raise HTTPException(
            status_code=404,
            detail="FIR draft not found. Please generate FIR first."
        )
    
    return fir_draft


@router.put("/draft/{case_id}", response_model=FIRDraftResponse)
async def update_fir_draft(
    case_id: str,
    fir_update: FIRDraftUpdate,
    db: Session = Depends(get_db)
):
    """
    Update FIR draft content.
    Allows officers to edit the generated FIR.
    
    Args:
        case_id: UUID of the case
        fir_update: Updated FIR content
        
    Returns:
        Updated FIR draft
    """
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    # Query FIR draft
    fir_draft = db.query(FIRDraft).filter(FIRDraft.case_id == case_uuid).first()
    
    if not fir_draft:
        raise HTTPException(
            status_code=404,
            detail="FIR draft not found. Please generate FIR first."
        )
    
    # Check if FIR can be edited
    if fir_draft.status == CaseStatusEnum.APPROVED:
        raise HTTPException(
            status_code=400,
            detail="Cannot edit an approved FIR"
        )
    
    # Update FIR content
    fir_draft.content = fir_update.content
    
    if fir_update.officer_notes:
        fir_draft.officer_notes = fir_update.officer_notes
    
    db.commit()
    db.refresh(fir_draft)
    
    return fir_draft


@router.post("/regenerate/{case_id}", response_model=FIRGenerateResponse)
async def regenerate_fir(
    case_id: str,
    request: FIRGenerateRequest = None,
    db: Session = Depends(get_db)
):
    """
    Regenerate FIR draft (overwrites existing).
    Use after entity corrections.
    
    Args:
        case_id: UUID of the case
        request: Optional additional info
        
    Returns:
        Regenerated FIR draft
    """
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    # Check if FIR is approved
    existing_fir = db.query(FIRDraft).filter(FIRDraft.case_id == case_uuid).first()
    
    if existing_fir and existing_fir.status == CaseStatusEnum.APPROVED:
        raise HTTPException(
            status_code=400,
            detail="Cannot regenerate an approved FIR"
        )
    
    # Use the generate endpoint
    return await generate_fir(case_id, request, db)
