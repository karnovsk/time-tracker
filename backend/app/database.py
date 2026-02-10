"""
Database configuration and session management.
Sets up async SQLAlchemy engine and session factory.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# Create async engine
engine = create_async_engine(
    settings.async_database_url,  # Use async URL (postgresql+asyncpg)
    echo=settings.debug,  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10,
    connect_args={
        "statement_cache_size": 0,  # Disable prepared statements for pgbouncer compatibility
        "server_settings": {
            "jit": "off",
            "timezone": "UTC"
        }
    }
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
