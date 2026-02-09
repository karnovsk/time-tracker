"""
Statistics API endpoints.
Handles calculation and retrieval of user statistics.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from datetime import date, timedelta
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.daily_entry import DailyEntry
from app.schemas.statistics import OverallStats, CategoryStats, TrendData
from app.dependencies import get_current_user

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/overview", response_model=OverallStats)
async def get_statistics_overview(
    period: Optional[str] = Query(None, description="Filter period: 'week', 'month', or None for all"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get overall statistics for the user.

    - period: 'week' (last 7 days), 'month' (last 30 days), or None (all time)
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

    # Get all entries
    result = await db.execute(query)
    entries = result.scalars().all()

    if not entries:
        # Return zero stats
        return OverallStats(
            casual_leisure=CategoryStats(total_hours=0, average_hours=0.0, entry_count=0),
            serious_leisure=CategoryStats(total_hours=0, average_hours=0.0, entry_count=0),
            project_leisure=CategoryStats(total_hours=0, average_hours=0.0, entry_count=0),
            total_entries=0,
            total_hours=0,
            average_total_hours=0.0,
            period=period
        )

    # Calculate statistics
    entry_count = len(entries)

    casual_total = sum(e.casual_leisure_hours for e in entries)
    serious_total = sum(e.serious_leisure_hours for e in entries)
    project_total = sum(e.project_leisure_hours for e in entries)
    total_hours = sum(e.total_hours for e in entries)

    return OverallStats(
        casual_leisure=CategoryStats(
            total_hours=casual_total,
            average_hours=round(casual_total / entry_count, 2),
            entry_count=entry_count
        ),
        serious_leisure=CategoryStats(
            total_hours=serious_total,
            average_hours=round(serious_total / entry_count, 2),
            entry_count=entry_count
        ),
        project_leisure=CategoryStats(
            total_hours=project_total,
            average_hours=round(project_total / entry_count, 2),
            entry_count=entry_count
        ),
        total_entries=entry_count,
        total_hours=total_hours,
        average_total_hours=round(total_hours / entry_count, 2),
        period=period
    )


@router.get("/trends", response_model=TrendData)
async def get_trends(
    days: int = Query(30, ge=7, le=365, description="Number of days to include in trends"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trend data for charts.

    - days: Number of days to include (7-365)
    """
    today = date.today()
    start_date = today - timedelta(days=days)

    # Get entries for the period
    result = await db.execute(
        select(DailyEntry)
        .where(
            DailyEntry.user_id == current_user.id,
            DailyEntry.entry_date >= start_date
        )
        .order_by(DailyEntry.entry_date.asc())
    )
    entries = result.scalars().all()

    # Build trend data
    dates = []
    casual_hours = []
    serious_hours = []
    project_hours = []
    total_hours = []

    for entry in entries:
        dates.append(entry.entry_date.isoformat())
        casual_hours.append(entry.casual_leisure_hours)
        serious_hours.append(entry.serious_leisure_hours)
        project_hours.append(entry.project_leisure_hours)
        total_hours.append(entry.total_hours)

    return TrendData(
        dates=dates,
        casual_hours=casual_hours,
        serious_hours=serious_hours,
        project_hours=project_hours,
        total_hours=total_hours
    )


@router.delete("/reset", status_code=204)
async def reset_user_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete all entries for the current user.
    This action cannot be undone!
    """
    # Delete all user's entries
    await db.execute(
        delete(DailyEntry)
        .where(DailyEntry.user_id == current_user.id)
    )

    # Reset user's last_entry_date
    current_user.last_entry_date = None

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset data: {str(e)}"
        )
