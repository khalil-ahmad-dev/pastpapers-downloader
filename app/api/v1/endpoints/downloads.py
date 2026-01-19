"""
API endpoints for bulk downloads.
"""
from fastapi import APIRouter, HTTPException, Path, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from pathlib import Path as PathLib
import json

from app.models.download import (
    BulkDownloadRequest,
    BulkDownloadResponse,
    DownloadProgress,
    JobStatus,
)
from app.services import download_service
from app.core.config import settings

router = APIRouter()


@router.post("/bulk", response_model=BulkDownloadResponse, status_code=202)
async def start_bulk_download(
    request: BulkDownloadRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a bulk download job.
    
    Args:
        request: Download request with subjects and seasons
        background_tasks: FastAPI background tasks
    
    Returns:
        Job ID and initial status
    """
    try:
        # Validate request
        if not request.subjects:
            raise HTTPException(status_code=400, detail="No subjects selected")
        
        if not request.seasons:
            raise HTTPException(status_code=400, detail="No seasons selected")
        
        # Create job IMMEDIATELY
        job_id = download_service.create_download_job(
            qualification=request.qualification,
            subjects=request.subjects,
            seasons=request.seasons,
            download_method="zip"  # Always ZIP
        )
        
        # Set initial status
        job = download_service.get_job_status(job_id)
        job["status"] = "initializing"
        job["message"] = "Starting download... Please wait."
        
        # Start download in background (this does all the heavy work)
        background_tasks.add_task(
            download_service.download_bulk_files,
            request.qualification,
            request.subjects,
            request.seasons,
            job_id
        )
        
        # Return IMMEDIATELY - don't wait for anything
        return BulkDownloadResponse(
            job_id=job_id,
            status="initializing",
            total_files=0,  # Will be updated by background task
            message="Starting download... Please wait.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting download: {str(e)}",
        )


@router.get("/{job_id}/progress", response_model=DownloadProgress)
async def get_download_progress(job_id: str):
    """
    Get the progress of a download job.
    
    Args:
        job_id: The job ID
    
    Returns:
        Current download progress
    """
    job = download_service.get_job_status(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found",
        )
    
    # Build progress response
    progress_data = {
        "job_id": job["job_id"],
        "status": job["status"],
        "current_file": job["current_file"],
        "total_files": job["total_files"],
        "percentage": job["percentage"],
        "message": job["message"],
        "downloaded_files": job["downloaded_files"],
        "failed_files": job["failed_files"],
        "errors": job["errors"],
        "zip_path": job.get("zip_path"),
        "zip_filename": job.get("zip_filename"),
    }
    
    # Add direct download URLs if available
    if job.get("direct_download_urls"):
        progress_data["direct_download_urls"] = job["direct_download_urls"]
    
    return DownloadProgress(**progress_data)


@router.get("/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Get complete job status.
    
    Args:
        job_id: The job ID
    
    Returns:
        Complete job status
    """
    job = download_service.get_job_status(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found",
        )
    
    return JobStatus(
        job_id=job["job_id"],
        qualification=job["qualification"],
        subjects=job["subjects"],
        seasons=job["seasons"],
        status=job["status"],
        current_file=job["current_file"],
        total_files=job["total_files"],
        percentage=job["percentage"],
        message=job["message"],
        downloaded_files=job["downloaded_files"],
        failed_files=job["failed_files"],
        errors=job["errors"],
        created_at=job["created_at"],
        started_at=job.get("started_at"),
        completed_at=job.get("completed_at"),
        zip_path=job.get("zip_path"),
        zip_filename=job.get("zip_filename"),
    )


@router.get("/{job_id}/zip")
async def download_zip(job_id: str, background_tasks: BackgroundTasks):
    """
    Download the ZIP file for a completed job.
    
    Args:
        job_id: The job ID
        background_tasks: FastAPI background tasks
    
    Returns:
        ZIP file download
    """
    job = download_service.get_job_status(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found",
        )
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed. Current status: {job['status']}",
        )
    
    zip_path = job.get("zip_path")
    if not zip_path:
        raise HTTPException(
            status_code=404,
            detail="ZIP file not found",
        )
    
    zip_file_path = PathLib(zip_path)
    if not zip_file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="ZIP file does not exist",
        )
    
    # Schedule cleanup after download (optional)
    # background_tasks.add_task(download_service.cleanup_job, job_id)
    
    return FileResponse(
        path=str(zip_file_path),
        filename=job.get("zip_filename", f"download_{job_id[:8]}.zip"),
        media_type="application/zip",
    )


@router.post("/direct", response_model=BulkDownloadResponse, status_code=202)
async def start_direct_download(
    request: BulkDownloadRequest,
    background_tasks: BackgroundTasks
):
    """
    Start direct file downloads (individual files, no ZIP).
    Creates a job and processes downloads in background with progress tracking.
    
    Args:
        request: Download request with subjects and seasons
        background_tasks: FastAPI background tasks
    
    Returns:
        Job ID and initial status
    """
    try:
        # Validate request
        if not request.subjects:
            raise HTTPException(status_code=400, detail="No subjects selected")
        
        if not request.seasons:
            raise HTTPException(status_code=400, detail="No seasons selected")
        
        # Create job for direct downloads
        job_id = download_service.create_download_job(
            qualification=request.qualification,
            subjects=request.subjects,
            seasons=request.seasons,
            download_method="direct"
        )
        
        # Start direct downloads in background
        background_tasks.add_task(
            download_service.download_direct_files,
            request.qualification,
            request.subjects,
            request.seasons,
            job_id
        )
        
        # Get initial job status
        job = download_service.get_job_status(job_id)
        
        return BulkDownloadResponse(
            job_id=job_id,
            status=job["status"],
            total_files=job["total_files"],
            message=job["message"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting direct download: {str(e)}",
        )


@router.post("/{job_id}/start-direct")
async def start_direct_downloads(job_id: str):
    """
    Mark direct download job as started.
    
    Args:
        job_id: The job ID
    
    Returns:
        Success message
    """
    job = download_service.get_job_status(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found",
        )
    
    job["status"] = "downloading"
    job["message"] = "Downloads started in browser..."
    
    return {"message": "Direct downloads started"}


@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job and clean up files.
    
    Args:
        job_id: The job ID
    
    Returns:
        Success message
    """
    job = download_service.get_job_status(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found",
        )
    
    download_service.cleanup_job(job_id)
    
    return {"message": f"Job '{job_id}' deleted successfully"}
