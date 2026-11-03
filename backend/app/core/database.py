import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

logger = logging.getLogger(__name__)


def build_async_engine(db_url: str) -> AsyncEngine:
    """
    Creates an asynchronous engine configured for either PostgreSQL (asyncpg)
    or SQLite (aiosqlite) with optimal pooling and connection parameters.
    """
    is_sqlite = db_url.startswith("sqlite")

    if is_sqlite:
        return create_async_engine(
            db_url,
            echo=settings.DEBUG,
            future=True,
            connect_args={"check_same_thread": False},
        )
    else:
        # PostgreSQL / asyncpg configuration
        return create_async_engine(
            db_url,
            echo=settings.DEBUG,
            future=True,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
        )


engine = build_async_engine(settings.DATABASE_URL)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
