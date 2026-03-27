# ── Backend Dockerfile ──────────────────────────────────────────────────────
# Uses Python 3.11-slim. Torch is installed CPU-only to keep the image lean.
# The HuggingFace NER model is downloaded on first startup (cached in a volume).
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim

# System deps needed by psycopg2-binary and reportlab
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
        libssl-dev \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (layer cache-friendly)
COPY requirements.txt .

# Install CPU-only torch separately to avoid pulling the CUDA wheel (saves ~2 GB)
RUN pip install --no-cache-dir torch==2.2.2+cpu \
        --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Create directories used at runtime
RUN mkdir -p uploads pdfs

# HuggingFace model cache — mount as a volume to persist across rebuilds
ENV TRANSFORMERS_CACHE=/app/.hf_cache
RUN mkdir -p /app/.hf_cache

EXPOSE 8000

# Run with uvicorn; DEBUG is controlled by the .env / compose env vars
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
