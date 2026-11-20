"""
Pariksha Copilot - Main Application Entrypoint
Exposes the FastAPI instance for Gunicorn + Uvicorn workers:
gunicorn -k uvicorn.workers.UvicornWorker -w 2 --timeout 180 -b 0.0.0.0:8000 main:app
"""
import os
import sys

# Ensure root directory is on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.server import app

__all__ = ["app"]
