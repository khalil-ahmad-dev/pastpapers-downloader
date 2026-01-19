"""
API endpoints for subjects.
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional

from app.models.subject import SubjectResponse, SubjectListResponse, SubjectDetailResponse
from app.services import subject_service

router = APIRouter()


@router.get("/", response_model=SubjectListResponse)
async def get_subjects(
    qualification: str = Query(..., description="Qualification ID (AICE, IGCSE, or O)"),
    search: Optional[str] = Query(None, description="Search term to filter subjects"),
):
    """
    Get all subjects for a specific qualification.
    
    Args:
        qualification: The qualification ID (AICE, IGCSE, or O)
        search: Optional search term to filter subjects
    
    Returns:
        List of subjects with codes and names.
    """
    try:
        subjects_data = subject_service.get_subjects_for_qualification(qualification, search)
        
        subjects = [
            SubjectResponse(
                code=subj["code"],
                name=subj["name"],
                url=subj["url"],
            )
            for subj in subjects_data
        ]
        
        return SubjectListResponse(
            subjects=subjects,
            total=len(subjects),
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
            detail=f"Error fetching subjects: {str(e)}",
        )


@router.get("/{syllabus_code}", response_model=SubjectDetailResponse)
async def get_subject(
    syllabus_code: str = Path(..., description="Syllabus code (e.g., 9700)"),
    qualification: str = Query(..., description="Qualification ID"),
):
    """
    Get a specific subject by syllabus code.
    
    Args:
        syllabus_code: The syllabus code (path parameter)
        qualification: The qualification ID (query parameter)
    
    Returns:
        Subject details.
    """
    try:
        subject = subject_service.get_subject_by_code(qualification, syllabus_code)
        
        if not subject:
            raise HTTPException(
                status_code=404,
                detail=f"Subject '{syllabus_code}' not found in qualification '{qualification}'",
            )
        
        return SubjectDetailResponse(
            code=subject["code"],
            name=subject["name"],
            url=subject["url"],
            qualification=qualification.upper(),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching subject: {str(e)}",
        )
