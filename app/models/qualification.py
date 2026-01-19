"""
Pydantic models for qualifications.
"""
from pydantic import BaseModel
from typing import List, Optional


class QualificationBase(BaseModel):
    """Base qualification model."""
    id: str
    name: str


class QualificationResponse(QualificationBase):
    """Qualification response model."""
    subject_count: int
    
    class Config:
        from_attributes = True


class QualificationListResponse(BaseModel):
    """List of qualifications response."""
    qualifications: List[QualificationResponse]
    total: int
