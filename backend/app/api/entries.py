"""
Daily entry API endpoints.
Handles submission and retrieval of daily leisure activity entries.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date, datetime, timedelta
from typing import Optional
from math import ceil
from app.database import get_db
from app.models.user import User
from app.models.daily_entry import DailyEntry
from app.schemas.entry import (
    DailyEntryCreate,
    DailyEntryResponse,
    CanSubmitResponse,
    EntryListResponse
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/entries", tags=["Daily Entries"])


@router.get("/can-submit", response_model=CanSubmitResponse)
async def can_submit_today(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if the current user can submit an entry for today.
    Returns existing entry if one already exists.
    """
    today = date.today()

    # Check if user already has an entry for today
    result = await db.execute(
        select(DailyEntry).where(
            DailyEntry.user_id == current_user.id,
            DailyEntry.entry_date == today
        )
    )
    existing_entry = result.scalar_one_or_none()

    if existing_entry:
        return CanSubmitResponse(
            can_submit=False,
            reason="You have already submitted an entry for today. Entries cannot be modified.",
            existing_entry=DailyEntryResponse.model_validate(existing_entry)
        )

    return CanSubmitResponse(
        can_submit=True,
        reason=None,
        existing_entry=None
    )


@router.post("/today", response_model=DailyEntryResponse, status_code=status.HTTP_201_CREATED)
async def submit_today_entry(
    entry_data: DailyEntryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit daily leisure activity entry.
    Only one entry per day is allowed and entries are immutable.
    Optionally specify entry_date to create entries for past dates (retroactive entry).
    """
    # Use provided date or default to today (allows retroactive entries)
    entry_date = entry_data.entry_date if entry_data.entry_date else date.today()

    # Validate total hours
    try:
        entry_data.validate_total()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Check if user already submitted for this date
    result = await db.execute(
        select(DailyEntry).where(
            DailyEntry.user_id == current_user.id,
            DailyEntry.entry_date == entry_date
        )
    )
    existing_entry = result.scalar_one_or_none()

    if existing_entry:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"You have already submitted an entry for {entry_date}. Only one entry per day is allowed."
        )

    # Create new entry
    new_entry = DailyEntry(
        user_id=current_user.id,
        entry_date=entry_date,
        casual_leisure_hours=entry_data.casual_leisure_hours,
        casual_leisure_note=entry_data.casual_leisure_note,
        serious_leisure_hours=entry_data.serious_leisure_hours,
        serious_leisure_note=entry_data.serious_leisure_note,
        project_leisure_hours=entry_data.project_leisure_hours,
        project_leisure_note=entry_data.project_leisure_note,
    )

    db.add(new_entry)

    # Update user's last_entry_date only if this is today's entry
    if entry_date == date.today():
        current_user.last_entry_date = entry_date

    try:
        await db.commit()
        await db.refresh(new_entry)
        return DailyEntryResponse.model_validate(new_entry)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create entry: {str(e)}"
        )


@router.get("/today", response_model=DailyEntryResponse)
async def get_today_entry(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current user's entry for today.
    Returns 404 if no entry exists for today.
    """
    today = date.today()

    result = await db.execute(
        select(DailyEntry).where(
            DailyEntry.user_id == current_user.id,
            DailyEntry.entry_date == today
        )
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No entry found for today"
        )

    return DailyEntryResponse.model_validate(entry)


@router.get("/history", response_model=EntryListResponse)
async def get_entry_history(
    period: Optional[str] = Query(None, description="Filter period: 'week', 'month', or None for all"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's entry history with optional filtering and pagination.

    - period: 'week' (last 7 days), 'month' (last 30 days), or None (all time)
    - page: Page number (1-indexed)
    - page_size: Number of entries per page (max 100)
    """
    # Build base query
    query = select(DailyEntry).where(DailyEntry.user_id == current_user.id)

    # Apply date filter
    today = date.today()
    if period == "week":
        start_date = today - timedelta(days=7)
        query = query.where(DailyEntry.entry_date >= start_date)
    elif period == "month":
        start_date = today - timedelta(days=30)
        query = query.where(DailyEntry.entry_date >= start_date)

    # Order by date descending (newest first)
    query = query.order_by(DailyEntry.entry_date.desc())

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    entries = result.scalars().all()

    # Calculate total pages
    total_pages = ceil(total / page_size) if total > 0 else 0

    return EntryListResponse(
        entries=[DailyEntryResponse.model_validate(entry) for entry in entries],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
