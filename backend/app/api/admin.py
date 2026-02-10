"""
Admin API endpoints for system-wide analytics.
Requires admin password authentication.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.dependencies import verify_admin_password
from app.models.user import User
from app.models.daily_entry import DailyEntry
from app.schemas.admin import UserStatsResponse, WordCloudResponse


router = APIRouter()


@router.get("/users-stats", response_model=List[UserStatsResponse])
async def get_all_users_stats(
    _: None = Depends(verify_admin_password),
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics for all users with their entry data.

    Requires X-Admin-Password header for authentication.

    Returns:
        List of user statistics including entry counts and cumulative hours
    """
    # 1. Get all users
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()

    user_stats = []
    for user in users:
        # 2. Get all entries for this user
        entries_result = await db.execute(
            select(DailyEntry).where(DailyEntry.user_id == user.id)
        )
        entries = entries_result.scalars().all()

        # 3. Aggregate totals
        casual_total = sum(e.casual_leisure_hours for e in entries)
        serious_total = sum(e.serious_leisure_hours for e in entries)
        project_total = sum(e.project_leisure_hours for e in entries)

        user_stats.append(UserStatsResponse(
            user_id=user.id,
            email=user.email,
            created_at=user.created_at,
            entry_count=len(entries),
            casual_total=casual_total,
            serious_total=serious_total,
            project_total=project_total,
            total_hours=casual_total + serious_total + project_total,
            leisure_distribution={
                "casual": casual_total,
                "serious": serious_total,
                "project": project_total
            }
        ))

    return user_stats


@router.get("/word-cloud-data", response_model=WordCloudResponse)
async def get_word_cloud_data(
    _: None = Depends(verify_admin_password),
    db: AsyncSession = Depends(get_db)
):
    """
    Get aggregated text from all users' notes for word cloud generation.

    Requires X-Admin-Password header for authentication.

    Returns:
        Combined text from all note fields across all entries
    """
    # Get all entries
    result = await db.execute(select(DailyEntry))
    entries = result.scalars().all()

    # Aggregate all notes
    all_notes = []
    for entry in entries:
        if entry.casual_leisure_note:
            all_notes.append(entry.casual_leisure_note)
        if entry.serious_leisure_note:
            all_notes.append(entry.serious_leisure_note)
        if entry.project_leisure_note:
            all_notes.append(entry.project_leisure_note)

    combined_text = " ".join(all_notes)

    return WordCloudResponse(
        combined_text=combined_text,
        total_entries=len(entries),
        total_notes=len(all_notes)
    )
