"""
Database package — models, engine, and seed logic.

Usage:
    from app.db import init_db, close_db, get_session_factory
    from app.core.repository.db_models import RuleRow, MetadataRow, Base
"""

from app.core.repository.db_models import Base, MetadataRow, RuleRow
from app.db.engine import close_db, init_db


def get_session_factory():
    """Return the current async session factory initialised by ``init_db``.

    This must be called after ``init_db()`` has completed; otherwise the
    returned factory will be ``None``.

    Returns:
        async_sessionmaker | None: The SQLAlchemy ``async_sessionmaker``
        bound to the application database engine, or ``None`` if
        ``init_db`` has not yet been called.
    """
    from app.db.engine import async_session_factory

    return async_session_factory


__all__ = [
    "Base",
    "MetadataRow",
    "RuleRow",
    "close_db",
    "get_session_factory",
    "init_db",
]
