"""
NER (Named Entity Recognition) Routes
Handles entity extraction from transcripts using multilingual BERT.
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.models import Case, Transcript, Entity
from schemas.schemas import (
    EntityResponse, EntityUpdate, NERExtractionRequest, NERExtractionResponse
)
from services.ner_service import ner_service


router = APIRouter()


@router.post("/extract/{case_id}", response_model=NERExtractionResponse)
async def extract_entities(
    case_id: str,
    request: NERExtractionRequest = None,
    db: Session = Depends(get_db)
):
    """
    Extract named entities from case transcript.
    
    Uses multilingual BERT to extract:
    - Person names
    - Locations
    - Dates
    - Incident description
    
    Args:
        case_id: UUID of the case
        request: Optional request with custom text to process
        
    Returns:
        Extracted entities stored in database
    """
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    # Get case
    case = db.query(Case).filter(Case.id == case_uuid).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get transcript text
    if request and request.text:
        # Use provided text
        text_to_process = request.text
    else:
        # Get text from stored transcript
        transcript = db.query(Transcript).filter(Transcript.case_id == case_uuid).first()
        if not transcript:
            raise HTTPException(status_code=404, detail="Transcript not found for this case")
        text_to_process = transcript.text
    
    # Extract entities using NER service
    try:
        extracted = await ner_service.extract_entities(
            text=text_to_process,
            language=case.language.value
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Entity extraction failed: {str(e)}"
        )
    
    # Check if entities already exist for this case
    existing_entity = db.query(Entity).filter(Entity.case_id == case_uuid).first()
    
    if existing_entity:
        # Update existing entity record
        existing_entity.person_names = extracted['person_names']
        existing_entity.locations = extracted['locations']
        existing_entity.dates = extracted['dates']
        existing_entity.incident = extracted['incident']
        existing_entity.raw_entities = extracted.get('raw_entities', [])
        
        db.commit()
        db.refresh(existing_entity)
        entity = existing_entity
    else:
        # Create new entity record
        new_entity = Entity(
            case_id=case_uuid,
            person_names=extracted['person_names'],
            locations=extracted['locations'],
            dates=extracted['dates'],
            incident=extracted['incident'],
            raw_entities=extracted.get('raw_entities', [])
        )
        db.add(new_entity)
        db.commit()
        db.refresh(new_entity)
        entity = new_entity
    
    return NERExtractionResponse(
        success=True,
        case_id=case_uuid,
        entities=EntityResponse.model_validate(entity)
    )


@router.get("/entities/{case_id}", response_model=EntityResponse)
async def get_entities(
    case_id: str,
    db: Session = Depends(get_db)
):
    """
    Get extracted entities for a case.
    
    Args:
        case_id: UUID of the case
        
    Returns:
        Stored entities for the case
    """
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    # Query entities
    entity = db.query(Entity).filter(Entity.case_id == case_uuid).first()
    
    if not entity:
        raise HTTPException(
            status_code=404,
            detail="Entities not found. Please run entity extraction first."
        )
    
    return entity


@router.put("/entities/{case_id}", response_model=EntityResponse)
async def update_entities(
    case_id: str,
    entity_update: EntityUpdate,
    db: Session = Depends(get_db)
):
    """
    Update/correct extracted entities.
    Allows officers to fix NER mistakes.
    
    Args:
        case_id: UUID of the case
        entity_update: Updated entity values
        
    Returns:
        Updated entity record
    """
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    # Query entities
    entity = db.query(Entity).filter(Entity.case_id == case_uuid).first()
    
    if not entity:
        raise HTTPException(
            status_code=404,
            detail="Entities not found. Please run entity extraction first."
        )
    
    # Update only provided fields
    if entity_update.person_names is not None:
        entity.person_names = entity_update.person_names
    
    if entity_update.locations is not None:
        entity.locations = entity_update.locations
    
    if entity_update.dates is not None:
        entity.dates = entity_update.dates
    
    if entity_update.incident is not None:
        entity.incident = entity_update.incident
    
    db.commit()
    db.refresh(entity)
    
    return entity


@router.delete("/entities/{case_id}")
async def delete_entities(
    case_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete extracted entities for a case.
    Allows re-extraction with different settings.
    
    Args:
        case_id: UUID of the case
    """
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    # Query and delete entities
    entity = db.query(Entity).filter(Entity.case_id == case_uuid).first()
    
    if not entity:
        raise HTTPException(status_code=404, detail="Entities not found")
    
    db.delete(entity)
    db.commit()
    
    return {"success": True, "message": "Entities deleted successfully"}
