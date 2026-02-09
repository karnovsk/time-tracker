"""
DailyEntry model - represents daily leisure activity entries.
Enforces one entry per user per day via UNIQUE constraint.
"""
from sqlalchemy import Column, Integer, Float, String, Date, DateTime, ForeignKey, UUID as SQLUUID, UniqueConstraint, CheckConstraint, Computed
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class DailyEntry(Base):
    """Daily leisure activity entry with hours and notes per category."""

    __tablename__ = "daily_entries"

    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(SQLUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    entry_date = Column(Date, nullable=False, index=True)

    # Casual leisure
    casual_leisure_hours = Column(Float, nullable=False)
    casual_leisure_note = Column(String, nullable=True)  # Optional activity description

    # Serious leisure
    serious_leisure_hours = Column(Float, nullable=False)
    serious_leisure_note = Column(String, nullable=True)

    # Project leisure
    project_leisure_hours = Column(Float, nullable=False)
    project_leisure_note = Column(String, nullable=True)

    # Computed total hours
    total_hours = Column(
        Float,
        Computed("casual_leisure_hours + serious_leisure_hours + project_leisure_hours"),
        nullable=False
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to user
    user = relationship("User", back_populates="entries")

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "entry_date", name="unique_user_date"),
        CheckConstraint("casual_leisure_hours >= 0", name="casual_hours_positive"),
        CheckConstraint("serious_leisure_hours >= 0", name="serious_hours_positive"),
        CheckConstraint("project_leisure_hours >= 0", name="project_hours_positive"),
        CheckConstraint(
            "casual_leisure_hours + serious_leisure_hours + project_leisure_hours > 0",
            name="total_hours_positive"
        ),
    )

    def __repr__(self):
        return f"<DailyEntry(user_id={self.user_id}, date={self.entry_date}, total={self.total_hours}h)>"
