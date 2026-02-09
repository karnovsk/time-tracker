"""
User model - represents users in the database.
Links to Supabase Auth via supabase_user_id.
"""
from sqlalchemy import Column, String, DateTime, Date, UUID as SQLUUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class User(Base):
    """User model linked to Supabase Auth."""

    __tablename__ = "users"

    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supabase_user_id = Column(SQLUUID(as_uuid=True), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_entry_date = Column(Date, nullable=True, index=True)  # For daily limit check

    # Relationship to daily entries
    entries = relationship("DailyEntry", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
