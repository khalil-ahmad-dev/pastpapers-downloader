"""
Service for fetching qualifications and their metadata.
"""
from app.core.links import RemoteLinks
from app.services import web_scraper, cache_service


QUALIFICATIONS = [
    {
        "id": "AICE",
        "name": "AS and A Level",
        "url": RemoteLinks.AICE.value,
        "pattern": RemoteLinks.AICE_PATTERN.value,
    },
    {
        "id": "IGCSE",
        "name": "IGCSE",
        "url": RemoteLinks.IGCSE.value,
        "pattern": RemoteLinks.IGCSE_PATTERN.value,
    },
    {
        "id": "O",
        "name": "O Level",
        "url": RemoteLinks.O.value,
        "pattern": RemoteLinks.O_PATTERN.value,
    },
]


def get_all_qualifications():
    """
    Get all available qualifications.
    Uses caching to avoid repeated scraping.
    
    Returns:
        List of qualification dictionaries with metadata.
    """
    # Check cache first
    cached_qualifications = cache_service.get_qualifications_cached()
    if cached_qualifications is not None:
        return cached_qualifications
    
    qualifications = []
    
    for qual in QUALIFICATIONS:
        try:
            # Get subject count for this qualification (only if not cached)
            subjects = web_scraper.get_exam_classes(qual["url"], qual["pattern"])
            subject_count = len(subjects)
            
            qualifications.append({
                "id": qual["id"],
                "name": qual["name"],
                "subject_count": subject_count,
            })
        except Exception as e:
            # If fetching fails, still return qualification with 0 count
            qualifications.append({
                "id": qual["id"],
                "name": qual["name"],
                "subject_count": 0,
            })
    
    # Cache the results
    cache_service.set_qualifications_cache(qualifications)
    
    return qualifications


def get_qualification_by_id(qualification_id: str):
    """
    Get a specific qualification by ID.
    
    Args:
        qualification_id: The qualification ID (AICE, IGCSE, or O)
    
    Returns:
        Qualification dictionary or None if not found.
    """
    for qual in QUALIFICATIONS:
        if qual["id"] == qualification_id:
            return qual
    return None
