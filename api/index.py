"""
Vercel serverless function entry point for FastAPI.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app
from app.main import app

# Vercel expects the app to be exported as 'app' for Python
# This is the ASGI application that Vercel will use
