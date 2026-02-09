"""
Schemas for statistics responses.
"""
from pydantic import BaseModel
from typing import Optional


class CategoryStats(BaseModel):
    """Statistics for a single leisure category."""
    total_hours: float
    average_hours: float
    entry_count: int


class OverallStats(BaseModel):
    """Overall statistics across all categories."""
    casual_leisure: CategoryStats
    serious_leisure: CategoryStats
    project_leisure: CategoryStats
    total_entries: int
    total_hours: float
    average_total_hours: float
    period: Optional[str] = None  # "week", "month", or "all"


class TrendData(BaseModel):
    """Trend data for charts."""
    dates: list[str]  # ISO format dates
    casual_hours: list[float]
    serious_hours: list[float]
    project_hours: list[float]
    total_hours: list[float]
