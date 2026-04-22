"""
Async database engine and session factory.

Uses SQLAlchemy 2.0 async with aiosqlite for SQLite.
To switch to PostgreSQL, change DATABASE_URL to:
    postgresql+asyncpg://user:pass@host:5432/dbname
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.repository.db_models import Base

logger = logging.getLogger("policy_engine.database")

# Module-level singletons (initialized by init_db)
engine = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_db(database_url: str) -> async_sessionmaker[AsyncSession]:
    """
    Initialize the async engine and create tables if they don't exist.

    For SQLite, enables WAL mode for high-concurrency reads.
    Returns the session factory for dependency injection.
    """
    global engine, async_session_factory

    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    engine = create_async_engine(
        database_url,
        echo=False,
        connect_args=connect_args,
    )

    async_session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Create tables (idempotent — safe to run every startup)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Enable WAL mode for SQLite high-read concurrency
    if database_url.startswith("sqlite"):
        async with engine.begin() as conn:
            await conn.exec_driver_sql("PRAGMA journal_mode=WAL")
            await conn.exec_driver_sql("PRAGMA synchronous=NORMAL")
        logger.info("SQLite WAL mode enabled")

    # One-time cleanup: remove legacy deploy_history from app_metadata
    # (deploy history now lives in its own table)
    async with async_session_factory() as session:
        from app.core.repository.db_models import MetadataRow

        row = await session.get(MetadataRow, "deploy_history")
        if row:
            await session.delete(row)
            await session.commit()
            logger.info("Migrated: removed legacy deploy_history from app_metadata")

    logger.info("Database initialized: %s", database_url.split("///")[0] + "///***")
    return async_session_factory


async def close_db() -> None:
    """Dispose the engine on shutdown."""
    if engine:
        await engine.dispose()
        logger.info("Database connection closed")
