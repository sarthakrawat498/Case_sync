"""
Audio Upload Routes
Handles audio file upload and transcription using Whisper.
"""

import os
import shutil
from uuid import uuid4
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.orm import Session

from database import get_db
from models.models import Case, Transcript, LanguageEnum
from schemas.schemas import AudioUploadResponse, CaseResponse, TranscriptResponse
from services.whisper_service import whisper_service
from core.config import settings


router = APIRouter()


@router.post("/audio", response_model=AudioUploadResponse)
async def upload_audio(
    file: UploadFile = File(..., description="Audio file to transcribe"),
    db: Session = Depends(get_db)
):
    """
    Upload audio file and transcribe using Whisper.
    
    Accepts audio files in formats: wav, mp3, m4a, webm, ogg, flac, mp4
    
    Returns:
    - case_id: Unique case identifier
    - transcript: Transcribed text
    - detected_language: Detected language (hi/en)
    """
    
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = ['.wav', '.mp3', '.m4a', '.webm', '.ogg', '.flac', '.mp4']
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Check file size (read content to check)
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB"
        )
    
    # Reset file pointer
    await file.seek(0)
    
    # Generate unique filename
    unique_filename = f"{uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    try:
        # Save uploaded file
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Transcribe audio using Whisper service
        transcription_result = await whisper_service.transcribe(file_path)
        
        transcript_text = transcription_result['text']
        detected_language = transcription_result['language']
        duration = transcription_result.get('duration', 0)
        
        # Map language code to enum
        language_enum = LanguageEnum.HINDI if detected_language == 'hi' else LanguageEnum.ENGLISH
        
        # Create Case record
        new_case = Case(
            language=language_enum
        )
        db.add(new_case)
        db.flush()  # Get the case ID
        
        # Create Transcript record
        new_transcript = Transcript(
            case_id=new_case.id,
            text=transcript_text,
            audio_filename=file.filename,
            duration_seconds=str(duration)
        )
        db.add(new_transcript)
        
        # Commit transaction
        db.commit()
        db.refresh(new_case)
        db.refresh(new_transcript)
        
        return AudioUploadResponse(
            success=True,
            message="Audio uploaded and transcribed successfully",
            case_id=new_case.id,
            transcript=transcript_text,
            detected_language=language_enum.value,
            audio_filename=file.filename
        )
        
    except Exception as e:
        # Rollback on error
        db.rollback()
        
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio: {str(e)}"
        )


@router.get("/transcript/{case_id}", response_model=TranscriptResponse)
async def get_transcript(
    case_id: str,
    db: Session = Depends(get_db)
):
    """
    Get transcript for a specific case.
    
    Args:
        case_id: UUID of the case
        
    Returns:
        Transcript details including text and metadata
    """
    from uuid import UUID
    
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    # Query transcript
    transcript = db.query(Transcript).filter(Transcript.case_id == case_uuid).first()
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    return transcript


@router.put("/transcript/{case_id}", response_model=TranscriptResponse)
async def update_transcript(
    case_id: str,
    text: str = Form(..., description="Updated transcript text"),
    db: Session = Depends(get_db)
):
    """
    Update transcript text (for corrections).
    
    Args:
        case_id: UUID of the case
        text: New transcript text
        
    Returns:
        Updated transcript
    """
    from uuid import UUID
    
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    # Query transcript
    transcript = db.query(Transcript).filter(Transcript.case_id == case_uuid).first()
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    # Update transcript
    transcript.text = text
    db.commit()
    db.refresh(transcript)
    
    return transcript


@router.delete("/audio/{case_id}")
async def delete_audio(
    case_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete audio file and case record.
    Only allowed if case is in DRAFT status.
    
    Args:
        case_id: UUID of the case
    """
    from uuid import UUID
    from models.models import CaseStatusEnum
    
    try:
        case_uuid = UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case ID format")
    
    # Query case
    case = db.query(Case).filter(Case.id == case_uuid).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check if case can be deleted (only DRAFT status)
    if case.status != CaseStatusEnum.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete case that is not in DRAFT status"
        )
    
    # Delete case (cascades to transcript, entities, fir_draft)
    db.delete(case)
    db.commit()
    
    return {"success": True, "message": "Case and associated data deleted"}
