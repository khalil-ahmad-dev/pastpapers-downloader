"""
Caching service for PapaCambridge data.
Reduces repeated scraping by caching seasons and file counts.
"""
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import json
from pathlib import Path

from app.core.config import settings


# In-memory cache
_seasons_cache: Dict[str, Dict] = {}  # {cache_key: {data, expires_at}}
_file_count_cache: Dict[str, Dict] = {}  # {url: {count, expires_at}}
_subjects_cache: Dict[str, Dict] = {}  # {qualification_id: {data, expires_at}}
_qualifications_cache: Optional[Dict] = None  # Cached qualifications list
_qualifications_cache_expires: Optional[datetime] = None


def get_cache_key(qualification: str, subject_code: str) -> str:
    """Generate cache key for seasons."""
    return f"{qualification}:{subject_code}"


def get_seasons_cached(qualification: str, subject_code: str) -> Optional[List[dict]]:
    """
    Get cached seasons data if available and not expired.
    
    Args:
        qualification: Qualification ID
        subject_code: Subject code
    
    Returns:
        Cached seasons list or None if not cached/expired
    """
    cache_key = get_cache_key(qualification, subject_code)
    
    if cache_key in _seasons_cache:
        cache_entry = _seasons_cache[cache_key]
        
        # Check if expired (cache for 1 hour)
        if datetime.now() < cache_entry["expires_at"]:
            return cache_entry["data"]
        else:
            # Remove expired entry
            del _seasons_cache[cache_key]
    
    return None


def set_seasons_cache(qualification: str, subject_code: str, seasons: List[dict], ttl_hours: int = 1):
    """
    Cache seasons data.
    
    Args:
        qualification: Qualification ID
        subject_code: Subject code
        seasons: Seasons data to cache
        ttl_hours: Time to live in hours (default: 1 hour)
    """
    cache_key = get_cache_key(qualification, subject_code)
    
    _seasons_cache[cache_key] = {
        "data": seasons,
        "expires_at": datetime.now() + timedelta(hours=ttl_hours),
    }


def get_file_count_cached(season_url: str) -> Optional[int]:
    """
    Get cached file count if available and not expired.
    
    Args:
        season_url: Season URL
    
    Returns:
        Cached file count or None if not cached/expired
    """
    if season_url in _file_count_cache:
        cache_entry = _file_count_cache[season_url]
        
        # Check if expired (cache for 24 hours - file counts change rarely)
        if datetime.now() < cache_entry["expires_at"]:
            return cache_entry["count"]
        else:
            # Remove expired entry
            del _file_count_cache[season_url]
    
    return None


def set_file_count_cache(season_url: str, count: int, ttl_hours: int = 24):
    """
    Cache file count.
    
    Args:
        season_url: Season URL
        count: File count to cache
        ttl_hours: Time to live in hours (default: 24 hours)
    """
    _file_count_cache[season_url] = {
        "count": count,
        "expires_at": datetime.now() + timedelta(hours=ttl_hours),
    }


def clear_cache():
    """Clear all cached data."""
    _seasons_cache.clear()
    _file_count_cache.clear()


def get_subjects_cached(qualification_id: str) -> Optional[List[dict]]:
    """
    Get cached subjects data if available and not expired.
    
    Args:
        qualification_id: Qualification ID
    
    Returns:
        Cached subjects list or None if not cached/expired
    """
    if qualification_id in _subjects_cache:
        cache_entry = _subjects_cache[qualification_id]
        
        # Check if expired (cache for 1 hour)
        if datetime.now() < cache_entry["expires_at"]:
            return cache_entry["data"]
        else:
            # Remove expired entry
            del _subjects_cache[qualification_id]
    
    return None


def set_subjects_cache(qualification_id: str, subjects: List[dict], ttl_hours: int = 1):
    """
    Cache subjects data.
    
    Args:
        qualification_id: Qualification ID
        subjects: Subjects data to cache
        ttl_hours: Time to live in hours (default: 1 hour)
    """
    _subjects_cache[qualification_id] = {
        "data": subjects,
        "expires_at": datetime.now() + timedelta(hours=ttl_hours),
    }


def get_qualifications_cached() -> Optional[List[dict]]:
    """
    Get cached qualifications data if available and not expired.
    
    Returns:
        Cached qualifications list or None if not cached/expired
    """
    global _qualifications_cache, _qualifications_cache_expires
    
    if _qualifications_cache is not None and _qualifications_cache_expires is not None:
        # Check if expired (cache for 1 hour)
        if datetime.now() < _qualifications_cache_expires:
            return _qualifications_cache
    
    return None


def set_qualifications_cache(qualifications: List[dict], ttl_hours: int = 1):
    """
    Cache qualifications data.
    
    Args:
        qualifications: Qualifications data to cache
        ttl_hours: Time to live in hours (default: 1 hour)
    """
    global _qualifications_cache, _qualifications_cache_expires
    
    _qualifications_cache = qualifications
    _qualifications_cache_expires = datetime.now() + timedelta(hours=ttl_hours)


def clear_expired_cache():
    """Remove expired cache entries."""
    now = datetime.now()
    
    # Clear expired seasons cache
    expired_keys = [
        key for key, entry in _seasons_cache.items()
        if now >= entry["expires_at"]
    ]
    for key in expired_keys:
        del _seasons_cache[key]
    
    # Clear expired file count cache
    expired_urls = [
        url for url, entry in _file_count_cache.items()
        if now >= entry["expires_at"]
    ]
    for url in expired_urls:
        del _file_count_cache[url]
    
    # Clear expired subjects cache
    expired_subjects = [
        qual_id for qual_id, entry in _subjects_cache.items()
        if now >= entry["expires_at"]
    ]
    for qual_id in expired_subjects:
        del _subjects_cache[qual_id]
    
    # Clear expired qualifications cache
    global _qualifications_cache, _qualifications_cache_expires
    if _qualifications_cache_expires and now >= _qualifications_cache_expires:
        _qualifications_cache = None
        _qualifications_cache_expires = None