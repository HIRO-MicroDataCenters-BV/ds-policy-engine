"""
Database viewer API — lightweight read-only DB inspection endpoints.

Provides table listing, row browsing, stats, and a read-only SQL query
runner for the dashboard DB Explorer tab.  Write operations (CRUD) are
done via the existing /api/v1/rules endpoints.

Tag: Database
"""

import logging
import re

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.repository.db_models import DeployHistoryRow, MetadataRow, RuleRow
from app.db import get_session_factory
from app.rest_api.response import error_response, success_response

logger = logging.getLogger("policy_engine.routes.db")

router = APIRouter(prefix="/api/v1/db", tags=["Database"])


def _get_session_factory():
    """Retrieve the async session factory for database access.

    This thin wrapper exists so that it can be easily overridden in tests
    via ``app.dependency_overrides``.

    Returns:
        async_sessionmaker: The SQLAlchemy async session factory initialised
        by ``init_db``.
    """
    return get_session_factory()


@router.get(
    "/stats",
    summary="Database statistics",
    description="Return high-level stats: table counts, DB engine info.",
)
async def db_stats():
    """Return high-level database statistics.

    Queries aggregate counts across all tables and identifies the database
    engine type from the configured URL.

    Returns:
        JSONResponse: A success envelope containing ``data.engine`` (database
        type), ``data.tables`` (per-table row counts including enabled/disabled
        breakdowns for rules), and ``data.roles_count`` (number of distinct
        roles).
    """
    sf = _get_session_factory()
    async with sf() as session:
        rules_count = (
            await session.execute(select(func.count(RuleRow.id)))
        ).scalar() or 0
        enabled_count = (
            await session.execute(
                select(func.count(RuleRow.id)).where(RuleRow.enabled.is_(True))
            )
        ).scalar() or 0
        disabled_count = rules_count - enabled_count
        meta_count = (
            await session.execute(select(func.count(MetadataRow.key)))
        ).scalar() or 0
        deploy_count = (
            await session.execute(select(func.count(DeployHistoryRow.id)))
        ).scalar() or 0

        # Get distinct roles
        roles_result = await session.execute(
            select(func.count(func.distinct(RuleRow.role)))
        )
        roles_count = roles_result.scalar() or 0

    from app.config import settings

    db_type = "SQLite" if "sqlite" in settings.database_url else "PostgreSQL"

    return success_response(
        data={
            "engine": db_type,
            "tables": {
                "rules": {
                    "total": rules_count,
                    "enabled": enabled_count,
                    "disabled": disabled_count,
                },
                "app_metadata": {"total": meta_count},
                "deploy_history": {"total": deploy_count},
            },
            "roles_count": roles_count,
        },
        message="Database statistics",
    )


@router.get(
    "/tables/rules",
    summary="Browse rules table",
    description="Return all rows from the rules table with full column data.",
)
async def browse_rules():
    """Return all rows from the rules table with full column data.

    Rows are ordered by creation date (ascending) and include every
    persisted column.

    Returns:
        JSONResponse: A success envelope containing ``data.rows`` (list of
        rule dicts with id, name, description, role, permissions, enabled,
        created_at, updated_at) and ``data.count`` (total row count).
    """
    sf = _get_session_factory()
    async with sf() as session:
        result = await session.execute(select(RuleRow).order_by(RuleRow.created_at))
        rows = result.scalars().all()
        data = [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "role": r.role,
                "permissions": r.permissions,
                "enabled": r.enabled,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            }
            for r in rows
        ]
    return success_response(
        data={"rows": data, "count": len(data)}, message="Rules table"
    )


@router.get(
    "/tables/metadata",
    summary="Browse metadata table",
    description="Return all key-value pairs from the app_metadata table.",
)
async def browse_metadata():
    """Return all key-value pairs from the app_metadata table.

    Rows are ordered alphabetically by key.

    Returns:
        JSONResponse: A success envelope containing ``data.rows`` (list of
        dicts with ``key`` and ``value`` fields) and ``data.count``.
    """
    sf = _get_session_factory()
    async with sf() as session:
        result = await session.execute(select(MetadataRow).order_by(MetadataRow.key))
        rows = result.scalars().all()
        data = [{"key": r.key, "value": r.value} for r in rows]
    return success_response(
        data={"rows": data, "count": len(data)}, message="Metadata table"
    )


@router.get(
    "/tables/deploy_history",
    summary="Browse deploy history table",
    description="Return all rows from the deploy_history table.",
)
async def browse_deploy_history():
    """Return all rows from the deploy_history table, newest first."""
    sf = _get_session_factory()
    async with sf() as session:
        result = await session.execute(
            select(DeployHistoryRow).order_by(DeployHistoryRow.id.desc())
        )
        rows = result.scalars().all()
        data = [
            {
                "id": r.id,
                "version": r.version,
                "deployed_at": r.deployed_at,
                "deployed_by": r.deployed_by,
                "rules_count": r.rules_count,
                "roles": r.roles,
            }
            for r in rows
        ]
    return success_response(
        data={"rows": data, "count": len(data)}, message="Deploy history table"
    )


# ---------------------------------------------------------------------------
# Read-only SQL query runner
# ---------------------------------------------------------------------------

# Only SELECT statements are allowed (case-insensitive, ignoring leading whitespace)
_SAFE_SQL = re.compile(r"^\s*SELECT\b", re.IGNORECASE)

# Dangerous keywords that must never appear even inside a SELECT
_BLOCKED = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|ATTACH|DETACH|PRAGMA\s+(?!table_info|database_list))\b",
    re.IGNORECASE,
)


class QueryRequest(BaseModel):
    """Request body for the SQL query runner."""

    sql: str
    limit: int = 200


@router.post(
    "/query",
    summary="Run read-only SQL query",
    description="Execute a read-only SELECT query against the database. "
    "Only SELECT statements are allowed; DML/DDL is rejected.",
)
async def run_query(body: QueryRequest):
    """Execute a read-only SQL query and return the result rows.

    The query must be a SELECT statement. INSERT, UPDATE, DELETE, DROP,
    ALTER, CREATE, and other write operations are rejected.

    Disabled by default — enable by setting ``DS__DB_QUERY_ENABLED=true``
    (dev/debug only). Exposing arbitrary SELECT to unauthenticated callers
    is a data-exfiltration + DoS surface even with SELECT-only guards.

    Args:
        body: QueryRequest with ``sql`` (the query) and ``limit`` (max rows, default 200).

    Returns:
        JSONResponse: A success envelope with ``data.columns`` (list of column names),
        ``data.rows`` (list of row dicts), and ``data.count``.
    """
    if not settings.db_query_enabled:
        logger.warning("Blocked /query call — DS__DB_QUERY_ENABLED=false")
        return error_response(
            code="ENDPOINT_DISABLED",
            message=(
                "The ad-hoc SQL query endpoint is disabled in this environment. "
                "Set DS__DB_QUERY_ENABLED=true to enable (dev/debug only)."
            ),
            status_code=403,
        )

    sql = body.sql.strip()

    if not _SAFE_SQL.match(sql):
        logger.warning("Blocked non-SELECT query attempt")
        return error_response(
            code="INVALID_QUERY",
            message="Only SELECT queries are allowed",
            status_code=400,
        )

    if _BLOCKED.search(sql):
        logger.warning("Blocked query with dangerous keywords")
        return error_response(
            code="BLOCKED_QUERY",
            message="Query contains blocked keywords (INSERT, UPDATE, DELETE, DROP, etc.)",
            status_code=400,
        )

    # Enforce row limit
    limit = min(body.limit, 1000)
    if "LIMIT" not in sql.upper():
        sql = sql.rstrip(";") + f" LIMIT {limit}"

    sf = _get_session_factory()
    try:
        async with sf() as session:
            result = await session.execute(text(sql))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
    except Exception as exc:
        logger.error("SQL query failed: %s", exc)
        return error_response(
            code="QUERY_ERROR",
            message=str(exc),
            status_code=400,
        )

    return success_response(
        data={"columns": columns, "rows": rows, "count": len(rows)},
        message=f"Query returned {len(rows)} row(s)",
    )
