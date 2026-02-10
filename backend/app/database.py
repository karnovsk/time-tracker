"""
Database configuration and session management.
Sets up async SQLAlchemy engine and session factory.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.config import settings

# Create async engine
# Using pooler with NullPool to avoid prepared statement cache issues with pgbouncer
engine = create_async_engine(
    settings.async_database_url,  # Use async URL (postgresql+asyncpg)
    echo=settings.debug,  # Log SQL queries in debug mode
    poolclass=NullPool,  # No pooling at SQLAlchemy level (pgbouncer handles it)
    connect_args={"statement_cache_size": 0}  # Disable prepared statements for pgbouncer
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency function to get database session.
    Yields a session and ensures it's closed after use.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database (create tables if not exists)."""
    async with engine.begin() as conn:
        # Import models to ensure they're registered
        from app.models import user, daily_entry  # noqa
        await conn.run_sync(Base.metadata.create_all)
