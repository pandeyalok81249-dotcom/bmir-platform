import pytest
from app.core.database import build_async_engine


def test_sqlite_engine_configuration():
    engine = build_async_engine("sqlite+aiosqlite:///./test_check.db")
    assert engine.dialect.name == "sqlite"
    assert engine.url.drivername == "sqlite+aiosqlite"
    assert "test_check.db" in str(engine.url)


def test_postgresql_engine_configuration():
    pg_url = "postgresql+asyncpg://postgres:password@localhost:5432/resume_intelligence"
    engine = build_async_engine(pg_url)
    assert engine.dialect.name == "postgresql"
    assert engine.pool.size() == 10

