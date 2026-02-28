"""Async SQLAlchemy 2.x database engine and session factory."""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Build async database URL (replace postgresql:// with postgresql+asyncpg://)
_db_url = str(settings.DATABASE_URL).replace(
    "postgresql://", "postgresql+asyncpg://"
)

# Engine with connection pooling
engine = create_async_engine(
    _db_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""

    pass


async def create_db_tables() -> None:
    """Create all tables defined in ORM models (for development use).

    In production use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async DB session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


__all__ = ["Base", "engine", "get_db", "AsyncSessionLocal"]
