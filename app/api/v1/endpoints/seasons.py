"""
API endpoints for seasons.
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional

from app.models.season import SeasonResponse, SeasonListResponse, SeasonDetailResponse
from app.services import season_service

router = APIRouter()


@router.get("/{syllabus_code}/seasons", response_model=SeasonListResponse)
async def get_seasons(
    syllabus_code: str = Path(..., description="Syllabus code (e.g., 9700)"),
    qualification: str = Query(..., description="Qualification ID (AICE, IGCSE, or O)"),
):
    """
    Get all seasons (years) for a specific subject.
    
    Args:
        syllabus_code: The syllabus code (path parameter)
        qualification: The qualification ID (query parameter)
    
    Returns:
        List of seasons with metadata (year, name, file_count).
    """
    try:
        seasons_data = season_service.get_seasons_for_subject(qualification, syllabus_code)
        
        seasons = [
            SeasonResponse(
                id=season["id"],
                name=season["name"],
                year=season["year"],
                url=season["url"],
                file_count=season["file_count"],
            )
            for season in seasons_data
        ]
        
        return SeasonListResponse(
            seasons=seasons,
            total=len(seasons),
            subject_code=syllabus_code,
            qualification=qualification.upper(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching seasons: {str(e)}",
        )


@router.get("/{syllabus_code}/seasons/{season_id}", response_model=SeasonDetailResponse)
async def get_season(
    syllabus_code: str = Path(..., description="Syllabus code"),
    season_id: str = Path(..., description="Season ID (name)"),
    qualification: str = Query(..., description="Qualification ID"),
):
    """
    Get a specific season by ID.
    
    Args:
        syllabus_code: The syllabus code
        season_id: The season ID (name)
        qualification: The qualification ID
    
    Returns:
        Season details.
    """
    try:
        season = season_service.get_season_by_id(qualification, syllabus_code, season_id)
        
        if not season:
            raise HTTPException(
                status_code=404,
                detail=f"Season '{season_id}' not found for subject '{syllabus_code}'",
            )
        
        return SeasonDetailResponse(
            id=season["id"],
            name=season["name"],
            year=season["year"],
            url=season["url"],
            file_count=season["file_count"],
            subject_code=syllabus_code,
            qualification=qualification.upper(),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching season: {str(e)}",
        )
