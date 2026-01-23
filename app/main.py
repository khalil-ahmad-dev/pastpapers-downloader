"""
FastAPI application entry point.
"""
import logging
import sys
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.core.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException

# Import API routers
from app.api.v1.api import api_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Set specific log levels for noisy libraries
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Past Papers Downloader - Web UI for downloading CAIE past papers",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Static files and templates
from pathlib import Path

base_path = Path(__file__).parent.parent
static_dir = base_path / "app" / "static"
templates_dir = base_path / "app" / "templates"

# Mount static files
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

templates = Jinja2Templates(directory=str(templates_dir))


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Landing page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/subjects", response_class=HTMLResponse)
async def subjects_page(request: Request):
    """Subjects selection page."""
    return templates.TemplateResponse("subjects.html", {"request": request})


@app.get("/seasons", response_class=HTMLResponse)
async def seasons_page(request: Request):
    """Seasons selection page."""
    return templates.TemplateResponse("seasons.html", {"request": request})


@app.get("/download", response_class=HTMLResponse)
async def download_page(request: Request):
    """Download progress page."""
    return templates.TemplateResponse("download.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Include API routers
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
