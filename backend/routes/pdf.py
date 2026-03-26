"""
PDF Generation Routes
Handles FIR PDF generation and download.
"""

import os
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import get_db
from models.models import Case, FIRDraft, Entity, CaseStatusEnum
from schemas.schemas import PDFGenerateResponse
from services.pdf_service import pdf_service


router = APIRouter()


@router.get("/generate/{case_id}")
async def generate_pdf(
    case_id: str,
    db: Session = Depends(get_db)
):
    """
    Generate and download FIR PDF.
    
    Args:
        case_id: UUID of the case
        
    Returns:
        PDF file download
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
    
    # Get complainant name from entities (for filename)
    entity = db.query(Entity).filter(Entity.case_id == case_uuid).first()
    complainant_name = None
    if entity and entity.person_names:
        complainant_name = entity.person_names[0]
    
    # Generate PDF
    try:
        pdf_path = pdf_service.generate_pdf(
            fir_content=fir_draft.content,
            case_id=str(case_uuid),
            language=case.language.value,
            complainant_name=complainant_name
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )
    
    # Return PDF file
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="PDF file not found after generation")
    
    filename = os.path.basename(pdf_path)
    
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/preview/{case_id}", response_model=PDFGenerateResponse)
async def preview_pdf_info(
    case_id: str,
    db: Session = Depends(get_db)
):
    """
    Get PDF generation preview info without actually generating.
    Useful for checking if PDF can be generated.
    
    Args:
        case_id: UUID of the case
        
    Returns:
        PDF generation status info
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
    
    # Check for existing PDF
    existing_pdf = pdf_service.get_pdf_path(str(case_uuid))
    
    return PDFGenerateResponse(
        success=True,
        case_id=case_uuid,
        filename=os.path.basename(existing_pdf) if existing_pdf else "Not generated",
        message="PDF can be generated" if not existing_pdf else "PDF already exists"
    )


@router.post("/regenerate/{case_id}")
async def regenerate_pdf(
    case_id: str,
    db: Session = Depends(get_db)
):
    """
    Regenerate PDF (overwrites existing).
    
    Args:
        case_id: UUID of the case
        
    Returns:
        New PDF file download
    """
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    # Delete existing PDF if any
    existing_pdf = pdf_service.get_pdf_path(str(case_uuid))
    if existing_pdf:
        pdf_service.delete_pdf(existing_pdf)
    
    # Generate new PDF using the main endpoint
    return await generate_pdf(case_id, db)


@router.delete("/{case_id}")
async def delete_pdf(
    case_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete generated PDF file.
    
    Args:
        case_id: UUID of the case
    """
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    # Find and delete PDF
    existing_pdf = pdf_service.get_pdf_path(str(case_uuid))
    
    if not existing_pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    success = pdf_service.delete_pdf(existing_pdf)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete PDF")
    
    return {"success": True, "message": "PDF deleted successfully"}
