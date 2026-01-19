"""
API router aggregation for v1.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import qualifications, subjects, seasons, downloads

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    qualifications.router,
    prefix="/qualifications",
    tags=["qualifications"],
)

api_router.include_router(
    subjects.router,
    prefix="/subjects",
    tags=["subjects"],
)

api_router.include_router(
    seasons.router,
    prefix="/subjects",
    tags=["seasons"],
)

api_router.include_router(
    downloads.router,
    prefix="/downloads",
    tags=["downloads"],
)
