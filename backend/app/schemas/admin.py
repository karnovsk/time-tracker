"""
Pydantic schemas for admin endpoints.
"""
from pydantic import BaseModel
from typing import Dict
from datetime import datetime
from uuid import UUID


class UserStatsResponse(BaseModel):
    """Statistics for a single user."""
    user_id: UUID
    email: str
    created_at: datetime
    entry_count: int
    casual_total: float
    serious_total: float
    project_total: float
    total_hours: float
    leisure_distribution: Dict[str, float]  # For pie chart

    model_config = {"from_attributes": True}


class WordCloudResponse(BaseModel):
    """Word cloud data from all users' notes."""
    combined_text: str
    total_entries: int
    total_notes: int

    model_config = {"from_attributes": True}
