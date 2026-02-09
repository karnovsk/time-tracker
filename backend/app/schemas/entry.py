"""
Schemas for daily entry requests and responses.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date, datetime
from uuid import UUID
from typing import Optional


class DailyEntryCreate(BaseModel):
    """Schema for creating a daily entry."""
    entry_date: Optional[date] = Field(None, description="Optional date for the entry (defaults to today). Allows retroactive entry submission.")
    casual_leisure_hours: float = Field(..., ge=0, description="Hours spent on casual leisure")
    casual_leisure_note: Optional[str] = Field(None, max_length=500, description="Notes about casual leisure activities")

    serious_leisure_hours: float = Field(..., ge=0, description="Hours spent on serious leisure")
    serious_leisure_note: Optional[str] = Field(None, max_length=500, description="Notes about serious leisure activities")

    project_leisure_hours: float = Field(..., ge=0, description="Hours spent on project leisure")
    project_leisure_note: Optional[str] = Field(None, max_length=500, description="Notes about project leisure activities")

    @field_validator('casual_leisure_hours', 'serious_leisure_hours', 'project_leisure_hours')
    @classmethod
    def validate_hours(cls, v: float) -> float:
        """Validate that hours are reasonable (0-24)."""
        if v < 0 or v > 24:
            raise ValueError('Hours must be between 0 and 24')
        return v

    @field_validator('casual_leisure_note', 'serious_leisure_note', 'project_leisure_note')
    @classmethod
    def validate_note(cls, v: Optional[str]) -> Optional[str]:
        """Trim whitespace from notes."""
        if v:
            v = v.strip()
            if not v:
                return None
        return v

    def validate_total(self) -> None:
        """Validate that total hours is greater than 0."""
        total = self.casual_leisure_hours + self.serious_leisure_hours + self.project_leisure_hours
        if total <= 0:
            raise ValueError('Total hours must be greater than 0')
        if total > 24:
            raise ValueError('Total hours cannot exceed 24')


class DailyEntryResponse(BaseModel):
    """Schema for daily entry response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    entry_date: date
    casual_leisure_hours: float
    casual_leisure_note: Optional[str]
    serious_leisure_hours: float
    serious_leisure_note: Optional[str]
    project_leisure_hours: float
    project_leisure_note: Optional[str]
    total_hours: float
    created_at: datetime


class CanSubmitResponse(BaseModel):
    """Schema for checking if user can submit today."""
    can_submit: bool
    reason: Optional[str] = None
    existing_entry: Optional[DailyEntryResponse] = None


class EntryListResponse(BaseModel):
    """Schema for paginated entry list."""
    entries: list[DailyEntryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
