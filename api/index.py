"""
Vercel Serverless Function Handler for FloodSight API

This module adapts the FastAPI application to run on Vercel's serverless platform.
"""
import sys
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from mangum import Mangum
from app.main import app

# Mangum adapter for AWS Lambda/Vercel compatibility
handler = Mangum(app, lifespan="off")

