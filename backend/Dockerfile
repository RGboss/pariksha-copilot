# ==============================================================
# Pariksha Copilot - Production Backend Dockerfile
# Base: python:3.12-slim | Non-root appuser | Gunicorn + Uvicorn
# ==============================================================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL="sqlite:////app/data/gov_exam_portal.db" \
    CHROMA_PERSIST_DIR="/app/data/chroma_db" \
    UPLOAD_DIR="/app/data/uploads"

WORKDIR /app

# Install system dependencies for build, PostgreSQL client, PyMuPDF, and healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root app user (UID 1000) and application runtime directories
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data /app/data/chroma_db /app/data/uploads /app/uploads && \
    chown -R appuser:appuser /app

# Copy application source code
COPY . /app/
RUN chown -R appuser:appuser /app

# Switch to non-root user for security
USER appuser

EXPOSE 8000

# Docker Healthcheck
HEALTHCHECK --interval=15s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch FastAPI application using Gunicorn + Uvicorn workers
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "--timeout", "180", "-b", "0.0.0.0:8000", "main:app"]
