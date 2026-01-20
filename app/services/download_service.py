"""
Service for bulk downloading past papers.
"""
import asyncio
import aiohttp
from pathlib import Path
from typing import List, Dict, Optional
import zipfile
import shutil
from datetime import datetime
import uuid
import json
import os

from app.services import web_scraper, subject_service, season_service
from app.core.config import settings


# In-memory job storage
download_jobs: Dict[str, Dict] = {}

# File-based storage path for local development
JOB_STORAGE_DIR = Path(settings.TEMP_DOWNLOAD_DIR) / "jobs"

# Create storage directory (for file-based fallback)
try:
    JOB_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
except (PermissionError, OSError):
    pass


async def download_file_async(session: aiohttp.ClientSession, url: str, filepath: Path, semaphore: asyncio.Semaphore):
    """
    Download a single file asynchronously.
    
    Args:
        session: aiohttp session
        url: File URL to download
        filepath: Path to save the file
        semaphore: Semaphore to limit concurrent downloads
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    async with semaphore:
        try:
            # Disable SSL verification for downloads (some servers have certificate issues)
            async with session.get(
                url, 
                timeout=aiohttp.ClientTimeout(total=settings.DOWNLOAD_TIMEOUT),
                ssl=False
            ) as response:
                if response.status == 200:
                    # Create parent directory if it doesn't exist
                    filepath.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Download file
                    with open(filepath, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    return True, None
                else:
                    return False, f"HTTP {response.status}"
        except asyncio.TimeoutError:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)


async def download_bulk_files(
    qualification: str,
    subjects: List[str],
    seasons: List[str],  # Format: "subjectCode:seasonId"
    job_id: str
) -> Dict:
    """
    Download all files for selected subjects and seasons.
    
    Args:
        qualification: Qualification ID
        subjects: List of subject codes
        seasons: List of season IDs in format "subjectCode:seasonId"
        job_id: Unique job ID
    
    Returns:
        Dictionary with download results
    """
    # Get job (from memory or file)
    job = get_job_status(job_id)
    if not job:
        raise ValueError(f"Job {job_id} not found")
    
    # Update job status
    job["status"] = "collecting_files"
    job["started_at"] = datetime.now().isoformat()
    job["message"] = "Collecting file URLs from website..."
    job["current_file"] = 0
    job["total_files"] = 0
    
    # Save to file system (for serverless)
    save_job_to_file(job_id, job)
    
    # Parse seasons into structured format
    season_map = {}  # {subjectCode: [seasonIds]}
    for season_key in seasons:
        subject_code, season_id = season_key.split(":", 1)
        if subject_code not in season_map:
            season_map[subject_code] = []
        season_map[subject_code].append(season_id)
    
    # Collect all file URLs
    all_files = []  # List of {url, filepath, subject_code, season_id, filename}
    total_files = 0
    
    for subject_code in subjects:
        # Get subject details
        subject = subject_service.get_subject_by_code(qualification, subject_code)
        if not subject:
            continue
        
        # Get seasons for this subject
        subject_seasons = season_map.get(subject_code, [])
        
        for season_id in subject_seasons:
            # Get season details
            season = season_service.get_season_by_id(qualification, subject_code, season_id)
            if not season:
                continue
            
            # Get all files for this season
            try:
                exams = web_scraper.get_exams(season["url"])
                
                for exam in exams:
                    # Create organized file path
                    # Structure: Subject-Code/Season-Name/filename.pdf
                    safe_subject_name = subject["name"].replace("/", "-").replace("\\", "-")
                    safe_season_name = season["name"].replace("/", "-").replace("\\", "-")
                    
                    filepath = Path(settings.TEMP_DOWNLOAD_DIR) / job_id / safe_subject_name / safe_season_name / exam.name
                    
                    all_files.append({
                        "url": exam.url,
                        "filepath": filepath,
                        "subject_code": subject_code,
                        "season_id": season_id,
                        "filename": exam.name,
                    })
                    total_files += 1
            except Exception as e:
                job["errors"].append(f"Error getting files for {subject_code}/{season_id}: {str(e)}")
    
    job["total_files"] = total_files
    job["message"] = f"Found {total_files} files. Starting downloads..."
    
    if total_files == 0:
        job["status"] = "failed"
        job["message"] = "No files found to download."
        save_job_to_file(job_id, job)
        return job
    
    job["status"] = "downloading"
    job["message"] = f"Downloading {total_files} files..."
    save_job_to_file(job_id, job)
    
    # Download files with concurrency limit
    semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_DOWNLOADS)
    downloaded_count = 0
    failed_count = 0
    
    # Create aiohttp session with SSL disabled (some servers have cert issues)
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        # Create download tasks with file info tracking
        async def download_with_tracking(file_info):
            """Download file and return result with file info."""
            success, error = await download_file_async(
                session,
                file_info["url"],
                file_info["filepath"],
                semaphore
            )
            return success, error, file_info
        
        # Create all download tasks
        download_tasks = [
            download_with_tracking(file_info) 
            for file_info in all_files
        ]
        
        # Process downloads concurrently using as_completed
        # This allows downloads to run in parallel (up to semaphore limit)
        # and we process results as they complete
        for coro in asyncio.as_completed(download_tasks):
            success, error, file_info = await coro
            downloaded_count += 1
            job["current_file"] = downloaded_count
            
            if success:
                job["downloaded_files"].append(file_info["filename"])
            else:
                failed_count += 1
                job["failed_files"].append({
                    "filename": file_info["filename"],
                    "error": error
                })
            
            # Update percentage
            if total_files > 0:
                job["percentage"] = (downloaded_count / total_files) * 100
            
            # Save job to file system periodically (every 10 files or on status change)
            if downloaded_count % 10 == 0 or downloaded_count == total_files:
                save_job_to_file(job_id, job)
    
    # Create ZIP archive
    job["status"] = "creating_zip"
    job["message"] = "Creating ZIP archive..."
    job["percentage"] = 95
    save_job_to_file(job_id, job)
    
    zip_path = create_zip_archive(job_id, subjects, qualification)
    
    job["status"] = "completed"
    job["completed_at"] = datetime.now().isoformat()
    job["zip_path"] = str(zip_path)
    job["zip_filename"] = zip_path.name
    job["percentage"] = 100
    job["message"] = f"Download complete! {downloaded_count} files downloaded, {failed_count} failed."
    
    # Save final job state
    save_job_to_file(job_id, job)
    
    return job


def create_zip_archive(job_id: str, subjects: List[str], qualification: str) -> Path:
    """
    Create a ZIP archive from downloaded files.
    
    Args:
        job_id: Job ID
        subjects: List of subject codes
        qualification: Qualification ID
    
    Returns:
        Path to created ZIP file
    """
    temp_dir = Path(settings.TEMP_DOWNLOAD_DIR) / job_id
    zip_filename = f"{qualification}_{job_id[:8]}.zip"
    zip_path = Path(settings.TEMP_DOWNLOAD_DIR) / zip_filename
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in temp_dir.rglob('*'):
            if file_path.is_file():
                # Get relative path for ZIP structure
                arcname = file_path.relative_to(temp_dir)
                zipf.write(file_path, arcname)
    
    return zip_path


def create_download_job(
    qualification: str, 
    subjects: List[str], 
    seasons: List[str],
    download_method: str = "zip"
) -> str:
    """
    Create a new download job (without starting it).
    Stores in both memory and file system for serverless compatibility.
    
    Args:
        qualification: Qualification ID
        subjects: List of subject codes
        seasons: List of season IDs in format "subjectCode:seasonId"
        download_method: "zip" or "direct"
    
    Returns:
        Job ID
    """
    job_id = str(uuid.uuid4())
    
    job_data = {
        "job_id": job_id,
        "qualification": qualification,
        "subjects": subjects,
        "seasons": seasons,
        "download_method": download_method,
        "status": "pending",
        "current_file": 0,
        "total_files": 0,
        "percentage": 0,
        "message": "Initializing download...",
        "downloaded_files": [],
        "failed_files": [],
        "errors": [],
        "created_at": datetime.now().isoformat(),
        "zip_path": None,
        "zip_filename": None,
        "direct_download_urls": [],  # For direct downloads
    }
    
    # Store in memory (for fast access)
    download_jobs[job_id] = job_data
    
    # Store in file system for persistence
    try:
        # Ensure directory exists
        JOB_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        
        job_file = JOB_STORAGE_DIR / f"{job_id}.json"
        with open(job_file, 'w') as f:
            json.dump(job_data, f)
            f.flush()  # Flush before closing
    except (PermissionError, OSError) as e:
        # If file storage fails, continue with memory only
        import logging
        logging.warning(f"Failed to save job to file: {e}")
        pass
    
    return job_id


def save_job_to_file(job_id: str, job_data: Dict):
    """
    Save job data to file system for persistence.
    
    Args:
        job_id: Job ID
        job_data: Job data dictionary
    """
    try:
        # Ensure directory exists
        JOB_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        
        job_file = JOB_STORAGE_DIR / f"{job_id}.json"
        
        # Write to temporary file first, then rename (atomic operation)
        temp_file = job_file.with_suffix('.tmp')
        
        with open(temp_file, 'w') as f:
            json.dump(job_data, f)
            f.flush()  # Flush before closing
        
        # Atomic rename (ensures file is complete)
        temp_file.replace(job_file)
        
        # Verify file was written
        if not job_file.exists():
            raise OSError(f"Job file {job_file} was not created")
            
    except (PermissionError, OSError) as e:
        # If file storage fails, continue with memory only
        import logging
        logging.warning(f"Failed to save job {job_id} to file: {e}")
        # Don't raise - allow fallback to memory
        pass


def get_job_status(job_id: str) -> Optional[Dict]:
    """
    Get the status of a download job.
    Checks memory first, then file system.
    
    Args:
        job_id: Job ID
    
    Returns:
        Job dictionary or None if not found.
    """
    # First check memory (fast access)
    if job_id in download_jobs:
        return download_jobs[job_id]
    
    # Then check file system
    try:
        job_file = JOB_STORAGE_DIR / f"{job_id}.json"
        if job_file.exists():
            with open(job_file, 'r') as f:
                job_data = json.load(f)
                # Also load into memory for faster subsequent access
                download_jobs[job_id] = job_data
                return job_data
        else:
            # File doesn't exist - log for debugging
            import logging
            logging.debug(f"Job file not found: {job_file} (dir exists: {JOB_STORAGE_DIR.exists()})")
    except (PermissionError, OSError, json.JSONDecodeError) as e:
        # Log error for debugging
        import logging
        logging.warning(f"Error reading job file {job_id}: {e}")
        pass
    
    return None


def cleanup_job(job_id: str):
    """
    Clean up temporary files for a job.
    
    Args:
        job_id: Job ID
    """
    if job_id in download_jobs:
        temp_dir = Path(settings.TEMP_DOWNLOAD_DIR) / job_id
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        
        # Keep job info for a while, but mark as cleaned
        download_jobs[job_id]["cleaned"] = True


async def download_direct_files(
    qualification: str,
    subjects: List[str],
    seasons: List[str],
    job_id: str
) -> Dict:
    """
    Prepare direct file downloads (no ZIP) with progress tracking.
    Collects file URLs and makes them available for browser download.
    
    Args:
        qualification: Qualification ID
        subjects: List of subject codes
        seasons: List of season IDs in format "subjectCode:seasonId"
        job_id: Unique job ID
    
    Returns:
        Dictionary with download job info
    """
    job = download_jobs[job_id]
    job["status"] = "collecting_files"
    job["started_at"] = datetime.now().isoformat()
    
    # Parse seasons into structured format
    season_map = {}
    for season_key in seasons:
        subject_code, season_id = season_key.split(":", 1)
        if subject_code not in season_map:
            season_map[subject_code] = []
        season_map[subject_code].append(season_id)
    
    # Collect all file URLs
    all_files = []
    total_files = 0
    
    job["status"] = "collecting_files"
    job["message"] = "Collecting file URLs..."
    
    for subject_code in subjects:
        subject = subject_service.get_subject_by_code(qualification, subject_code)
        if not subject:
            continue
        
        subject_seasons = season_map.get(subject_code, [])
        
        for season_id in subject_seasons:
            season = season_service.get_season_by_id(qualification, subject_code, season_id)
            if not season:
                continue
            
            try:
                exams = web_scraper.get_exams(season["url"])
                
                for exam in exams:
                    all_files.append({
                        "url": exam.url,
                        "filename": exam.name,
                        "subject": subject["name"],
                        "subject_code": subject_code,
                        "season": season["name"],
                    })
                    total_files += 1
            except Exception as e:
                job["errors"].append(f"Error getting files for {subject_code}/{season_id}: {str(e)}")
    
    job["total_files"] = total_files
    job["status"] = "ready"
    job["message"] = f"Ready to download {total_files} files. Click 'Start Download' to begin."
    job["direct_download_urls"] = all_files
    
    save_job_to_file(job_id, job)
    
    return job


def get_direct_download_urls(
    qualification: str,
    subjects: List[str],
    seasons: List[str],
) -> List[Dict[str, str]]:
    """
    Get direct download URLs for files (without downloading or creating ZIP).
    Helper function for getting URLs only.
    
    Args:
        qualification: Qualification ID
        subjects: List of subject codes
        seasons: List of season IDs in format "subjectCode:seasonId"
    
    Returns:
        List of dictionaries with file info: {url, filename, subject, season}
    """
    # Parse seasons into structured format
    season_map = {}
    for season_key in seasons:
        subject_code, season_id = season_key.split(":", 1)
        if subject_code not in season_map:
            season_map[subject_code] = []
        season_map[subject_code].append(season_id)
    
    file_urls = []
    
    for subject_code in subjects:
        subject = subject_service.get_subject_by_code(qualification, subject_code)
        if not subject:
            continue
        
        subject_seasons = season_map.get(subject_code, [])
        
        for season_id in subject_seasons:
            season = season_service.get_season_by_id(qualification, subject_code, season_id)
            if not season:
                continue
            
            try:
                exams = web_scraper.get_exams(season["url"])
                
                for exam in exams:
                    file_urls.append({
                        "url": exam.url,
                        "filename": exam.name,
                        "subject": subject["name"],
                        "subject_code": subject_code,
                        "season": season["name"],
                    })
            except Exception as e:
                continue
    
    return file_urls
