"""
API endpoints for qualifications.
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.models.qualification import QualificationResponse, QualificationListResponse
from app.services import qualification_service

router = APIRouter()


@router.get("/", response_model=QualificationListResponse)
async def get_qualifications():
    """
    Get all available qualifications (A-Level, IGCSE, O-Level).
    
    Returns:
        List of qualifications with subject counts.
    """
    try:
        qualifications_data = qualification_service.get_all_qualifications()
        
        qualifications = [
            QualificationResponse(
                id=qual["id"],
                name=qual["name"],
                subject_count=qual["subject_count"],
            )
            for qual in qualifications_data
        ]
        
        return QualificationListResponse(
            qualifications=qualifications,
            total=len(qualifications),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching qualifications: {str(e)}",
        )


@router.get("/{qualification_id}", response_model=dict)
async def get_qualification(qualification_id: str):
    """
    Get a specific qualification by ID.
    
    Args:
        qualification_id: The qualification ID (AICE, IGCSE, or O)
    
    Returns:
        Qualification details.
    """
    qualification = qualification_service.get_qualification_by_id(qualification_id.upper())
    
    if not qualification:
        raise HTTPException(
            status_code=404,
            detail=f"Qualification '{qualification_id}' not found",
        )
    
    return qualification
