"""
CaseSync Database Models
SQLAlchemy ORM models for the FIR generation system.

Tables:
- Case: Main case record with language and status
- Transcript: Audio transcription text
- Entity: Extracted named entities (persons, locations, dates)
- FIRDraft: Generated FIR content with review status
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, DateTime, Enum, ForeignKey, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from database import Base


class LanguageEnum(str, enum.Enum):
    """Supported languages for FIR generation."""
    HINDI = "hi"
    ENGLISH = "en"


class CaseStatusEnum(str, enum.Enum):
    """Case status lifecycle states."""
    DRAFT = "DRAFT"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Case(Base):
    """
    Main case record that ties together all related data.
    Each audio upload creates a new case.
    """
    __tablename__ = "cases"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    language = Column(
        Enum(LanguageEnum),
        nullable=False,
        default=LanguageEnum.ENGLISH,
        comment="Detected language of the audio (hi/en)"
    )
    status = Column(
        Enum(CaseStatusEnum),
        nullable=False,
        default=CaseStatusEnum.DRAFT,
        comment="Current case status in the review workflow"
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    transcript = relationship(
        "Transcript",
        back_populates="case",
        uselist=False,
        cascade="all, delete-orphan"
    )
    entities = relationship(
        "Entity",
        back_populates="case",
        uselist=False,
        cascade="all, delete-orphan"
    )
    fir_draft = relationship(
        "FIRDraft",
        back_populates="case",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Case(id={self.id}, language={self.language}, status={self.status})>"


class Transcript(Base):
    """
    Stores the raw transcription from Whisper ASR.
    One transcript per case.
    """
    __tablename__ = "transcripts"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    case_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    text = Column(
        Text,
        nullable=False,
        comment="Full transcribed text from audio"
    )
    audio_filename = Column(
        String(255),
        nullable=True,
        comment="Original audio filename"
    )
    duration_seconds = Column(
        String(50),
        nullable=True,
        comment="Audio duration in seconds"
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationship back to case
    case = relationship("Case", back_populates="transcript")
    
    def __repr__(self):
        return f"<Transcript(id={self.id}, case_id={self.case_id})>"


class Entity(Base):
    """
    Stores extracted named entities from the transcript.
    Uses JSON columns for flexible entity storage.
    """
    __tablename__ = "entities"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    case_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    person_names = Column(
        JSON,
        nullable=False,
        default=list,
        comment="List of extracted person names"
    )
    locations = Column(
        JSON,
        nullable=False,
        default=list,
        comment="List of extracted locations/places"
    )
    dates = Column(
        JSON,
        nullable=False,
        default=list,
        comment="List of extracted dates/times"
    )
    incident = Column(
        Text,
        nullable=True,
        comment="Extracted incident description/summary"
    )
    raw_entities = Column(
        JSON,
        nullable=True,
        comment="Raw NER output for debugging"
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationship back to case
    case = relationship("Case", back_populates="entities")
    
    def __repr__(self):
        return f"<Entity(id={self.id}, case_id={self.case_id})>"


class FIRDraft(Base):
    """
    Stores the generated FIR draft content.
    Tracks review status and modifications.
    """
    __tablename__ = "fir_drafts"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    case_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    content = Column(
        Text,
        nullable=False,
        comment="Full FIR draft content"
    )
    status = Column(
        Enum(CaseStatusEnum),
        nullable=False,
        default=CaseStatusEnum.DRAFT,
        comment="FIR draft status (mirrors case status)"
    )
    officer_notes = Column(
        Text,
        nullable=True,
        comment="Officer review notes/comments"
    )
    reviewed_by = Column(
        String(255),
        nullable=True,
        comment="Name/ID of reviewing officer"
    )
    approved_by = Column(
        String(255),
        nullable=True,
        comment="Name/ID of approving officer"
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationship back to case
    case = relationship("Case", back_populates="fir_draft")
    
    def __repr__(self):
        return f"<FIRDraft(id={self.id}, case_id={self.case_id}, status={self.status})>"
