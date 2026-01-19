"""
Pydantic models for seasons.
"""
from pydantic import BaseModel
from typing import List, Optional


class SeasonBase(BaseModel):
    """Base season model."""
    id: str
    name: str
    year: int
    url: str
    file_count: int


class SeasonResponse(SeasonBase):
    """Season response model."""
    
    class Config:
        from_attributes = True


class SeasonListResponse(BaseModel):
    """List of seasons response."""
    seasons: List[SeasonResponse]
    total: int
    subject_code: str
    qualification: str


class SeasonDetailResponse(SeasonBase):
    """Season detail response."""
    subject_code: str
    qualification: str
    
    class Config:
        from_attributes = True
