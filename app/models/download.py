"""
Pydantic models for bulk downloads.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict


class BulkDownloadRequest(BaseModel):
    """Request model for starting a bulk download."""
    qualification: str
    subjects: List[str]
    seasons: List[str]  # Format: "subjectCode:seasonId"
    download_method: Optional[str] = "zip"  # "zip" or "direct"


class BulkDownloadResponse(BaseModel):
    """Response model for starting a bulk download."""
    job_id: str
    status: str
    total_files: int
    message: str


class DownloadProgress(BaseModel):
    """Progress model for download status."""
    job_id: str
    status: str
    current_file: int
    total_files: int
    percentage: float
    message: str
    downloaded_files: List[str]
    failed_files: List[Dict]
    errors: List[str]
    zip_path: Optional[str] = None
    zip_filename: Optional[str] = None
    direct_download_urls: Optional[List[Dict]] = None


class JobStatus(BaseModel):
    """Complete job status model."""
    job_id: str
    qualification: str
    subjects: List[str]
    seasons: List[str]
    status: str
    current_file: int
    total_files: int
    percentage: float
    message: str
    downloaded_files: List[str]
    failed_files: List[Dict]
    errors: List[str]
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    zip_path: Optional[str] = None
    zip_filename: Optional[str] = None
