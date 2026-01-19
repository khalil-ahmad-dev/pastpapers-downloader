"""
Pydantic models for subjects.
"""
from pydantic import BaseModel
from typing import List, Optional


class SubjectBase(BaseModel):
    """Base subject model."""
    code: str
    name: str
    url: str


class SubjectResponse(SubjectBase):
    """Subject response model."""
    
    class Config:
        from_attributes = True


class SubjectListResponse(BaseModel):
    """List of subjects response."""
    subjects: List[SubjectResponse]
    total: int
    qualification: str


class SubjectDetailResponse(SubjectBase):
    """Subject detail response."""
    qualification: str
    
    class Config:
        from_attributes = True
