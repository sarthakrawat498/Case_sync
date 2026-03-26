"""
CaseSync Database Module
Handles SQLAlchemy engine, session management, and database dependencies.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from core.config import settings


# Create SQLAlchemy engine 
# Different settings for SQLite vs PostgreSQL
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite settings
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        echo=settings.DEBUG,  # Log SQL queries in debug mode
        connect_args={"check_same_thread": False}  # Required for SQLite
    )
else:
    # PostgreSQL settings
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.DEBUG  # Log SQL queries in debug mode
    )

# SessionLocal class for creating database sessions
# autocommit=False: Manual transaction control
# autoflush=False: Manual flush control for better performance
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    Ensures proper cleanup after request completion.
    
    Usage in routes:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.
    Called during application startup.
    """
    # Import all models to ensure they are registered with Base
    from models import models  # noqa: F401
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


def drop_db() -> None:
    """
    Drop all database tables.
    Use with caution - only for development/testing.
    """
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped.")
