"""
CaseSync - AI-Powered FIR Generation System
Main FastAPI Application Entry Point

This system supports Hindi and English language processing for
Indian law enforcement FIR (First Information Report) generation.

Pipeline: Audio Input → Whisper ASR → BERT NER → FIR Draft → Officer Review → PDF Output
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from core.config import settings
from database import init_db

# Import routers
from routes import upload, ner, fir, review, pdf


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup: Initialize database
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    print("Application startup complete.")
    
    yield  # Application runs here
    
    # Shutdown: Cleanup resources
    print("Application shutting down...")


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## CaseSync - AI-Powered FIR Generation System
    
    A production-ready application for Indian law enforcement that automates
    First Information Report (FIR) generation from audio recordings.
    
    ### Features:
    - **Multilingual Support**: Hindi and English audio processing
    - **Speech-to-Text**: Whisper-based audio transcription
    - **Entity Extraction**: BERT-based Named Entity Recognition
    - **Template-Based FIR**: Deterministic FIR generation (no hallucination)
    - **Officer Review**: Edit, review, and approve workflow
    - **PDF Export**: Professional FIR document generation
    
    ### Supported Languages:
    - English (en)
    - Hindi (hi)
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers for monitoring."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    Logs the error and returns a generic error response.
    """
    # In production, log to monitoring service
    print(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An internal server error occurred.",
            "detail": str(exc) if settings.DEBUG else None
        }
    )


# Include API routers with prefixes
app.include_router(
    upload.router,
    prefix="/api/upload",
    tags=["Audio Upload"]
)

app.include_router(
    ner.router,
    prefix="/api/ner",
    tags=["Entity Extraction"]
)

app.include_router(
    fir.router,
    prefix="/api/fir",
    tags=["FIR Generation"]
)

app.include_router(
    review.router,
    prefix="/api/review",
    tags=["Officer Review"]
)

app.include_router(
    pdf.router,
    prefix="/api/pdf",
    tags=["PDF Generation"]
)


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns application status and version.
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "speech_service": "deepgram_api"
    }


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "documentation": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
