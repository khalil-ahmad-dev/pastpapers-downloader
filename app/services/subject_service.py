"""
Service for fetching subjects for a qualification.
"""
from typing import List, Optional

from app.core.links import RemoteLinks
from app.services import web_scraper, cache_service
from app.services.qualification_service import get_qualification_by_id


def get_subjects_for_qualification(qualification_id: str, search: Optional[str] = None) -> List[dict]:
    """
    Get all subjects for a specific qualification.
    Uses caching to avoid repeated scraping.
    
    Args:
        qualification_id: The qualification ID (AICE, IGCSE, or O)
        search: Optional search term to filter subjects
    
    Returns:
        List of subject dictionaries with code, name, and URL.
    """
    # Check cache first
    cached_subjects = cache_service.get_subjects_cached(qualification_id.upper())
    if cached_subjects is not None:
        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            return [
                subject for subject in cached_subjects
                if search_lower in subject["name"].lower() or search_lower in subject["code"].lower()
            ]
        return cached_subjects
    
    qualification = get_qualification_by_id(qualification_id.upper())
    
    if not qualification:
        raise ValueError(f"Qualification '{qualification_id}' not found")
    
    try:
        # Get subjects using web scraper (only if not cached)
        subjects = web_scraper.get_exam_classes(qualification["url"], qualification["pattern"])
        
        # Convert to list of dictionaries
        subject_list = []
        for subject in subjects:
            # Extract syllabus code from name (e.g., "Biology - 9700" -> "9700")
            code = extract_syllabus_code(subject.name)
            
            subject_dict = {
                "code": code,
                "name": subject.name,
                "url": subject.url,
            }
            
            subject_list.append(subject_dict)
        
        # Cache the results (before filtering)
        cache_service.set_subjects_cache(qualification_id.upper(), subject_list)
        
        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            return [
                subject for subject in subject_list
                if search_lower in subject["name"].lower() or search_lower in subject["code"].lower()
            ]
        
        return subject_list
    except Exception as e:
        raise Exception(f"Error fetching subjects: {str(e)}")


def get_subject_by_code(qualification_id: str, syllabus_code: str) -> Optional[dict]:
    """
    Get a specific subject by syllabus code.
    
    Args:
        qualification_id: The qualification ID
        syllabus_code: The syllabus code (e.g., "9700")
    
    Returns:
        Subject dictionary or None if not found.
    """
    subjects = get_subjects_for_qualification(qualification_id)
    
    for subject in subjects:
        if subject["code"] == syllabus_code:
            return subject
    
    return None


def extract_syllabus_code(subject_name: str) -> str:
    """
    Extract syllabus code from subject name.
    
    Examples:
        "Biology - 9700" -> "9700"
        "Chemistry - 9701" -> "9701"
        "English - 9093" -> "9093"
    
    Args:
        subject_name: The subject name string
    
    Returns:
        Syllabus code as string, or empty string if not found.
    """
    # Try to find 4-digit number (most common format)
    import re
    match = re.search(r'\b(\d{4})\b', subject_name)
    if match:
        return match.group(1)
    
    # Try to find any number sequence
    match = re.search(r'(\d+)', subject_name)
    if match:
        return match.group(1)
    
    # If no code found, return empty string
    return ""
