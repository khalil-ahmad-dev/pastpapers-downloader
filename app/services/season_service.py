"""
Service for fetching seasons (years) for a subject.
"""
from typing import List, Optional
import re

from app.services import web_scraper, subject_service, cache_service


def get_seasons_for_subject(qualification_id: str, syllabus_code: str) -> List[dict]:
    """
    Get all seasons (years) for a specific subject.
    Uses caching to avoid repeated scraping.
    
    Args:
        qualification_id: The qualification ID (AICE, IGCSE, or O)
        syllabus_code: The syllabus code (e.g., "9700")
    
    Returns:
        List of season dictionaries with id, name, year, and file_count.
    """
    # Check cache first
    cached_seasons = cache_service.get_seasons_cached(qualification_id, syllabus_code)
    if cached_seasons is not None:
        return cached_seasons
    
    # Get subject to get the URL
    subject = subject_service.get_subject_by_code(qualification_id, syllabus_code)
    
    if not subject:
        raise ValueError(f"Subject '{syllabus_code}' not found in qualification '{qualification_id}'")
    
    try:
        # Get seasons using web scraper (only if not cached)
        seasons = web_scraper.get_exam_seasons(subject["url"])
        
        # Convert to list of dictionaries with metadata
        season_list = []
        for season in seasons:
            # Extract year from season name
            year = extract_year_from_season(season.name)
            
            # Get file count for this season (uses cache)
            file_count = get_season_file_count(season.url)
            
            season_dict = {
                "id": season.name,
                "name": season.name,
                "year": year,
                "url": season.url,
                "file_count": file_count,
            }
            
            season_list.append(season_dict)
        
        # Sort by year (newest first)
        season_list.sort(key=lambda x: x["year"], reverse=True)
        
        # Cache the results
        cache_service.set_seasons_cache(qualification_id, syllabus_code, season_list)
        
        return season_list
    except Exception as e:
        raise Exception(f"Error fetching seasons: {str(e)}")


def get_season_file_count(season_url: str) -> int:
    """
    Get the number of files available for a season.
    Uses caching to avoid repeated scraping.
    
    Args:
        season_url: The URL of the season page
    
    Returns:
        Number of files available.
    """
    # Check cache first
    cached_count = cache_service.get_file_count_cached(season_url)
    if cached_count is not None:
        return cached_count
    
    try:
        exams = web_scraper.get_exams(season_url)
        count = len(exams)
        
        # Cache the result
        cache_service.set_file_count_cache(season_url, count)
        
        return count
    except Exception:
        # If fetching fails, return 0
        return 0


def extract_year_from_season(season_name: str) -> int:
    """
    Extract year from season name.
    
    Examples:
        "2024-May-June" -> 2024
        "2023-Oct-Nov" -> 2023
        "2001 Nov" -> 2001
    
    Args:
        season_name: The season name string
    
    Returns:
        Year as integer, or 0 if not found.
    """
    # Try to find 4-digit year
    match = re.search(r'\b(20\d{2})\b', season_name)
    if match:
        return int(match.group(1))
    
    # Try to find 2-digit year (assume 2000s)
    match = re.search(r'\b(\d{2})\b', season_name)
    if match:
        year = int(match.group(1))
        if year < 50:  # Assume 2000s
            return 2000 + year
        else:  # Assume 1900s
            return 1900 + year
    
    return 0


def get_season_by_id(qualification_id: str, syllabus_code: str, season_id: str) -> Optional[dict]:
    """
    Get a specific season by ID.
    
    Args:
        qualification_id: The qualification ID
        syllabus_code: The syllabus code
        season_id: The season ID (name)
    
    Returns:
        Season dictionary or None if not found.
    """
    seasons = get_seasons_for_subject(qualification_id, syllabus_code)
    
    for season in seasons:
        if season["id"] == season_id:
            return season
    
    return None
