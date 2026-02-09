"""
Script to create database tables directly using SQLAlchemy.
Workaround for Windows timezone issues with Alembic.
"""
import asyncio
from app.database import engine, Base
from app.models import User, DailyEntry  # noqa - Import models


async def create_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        # Drop all tables (be careful in production!)
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_tables())
