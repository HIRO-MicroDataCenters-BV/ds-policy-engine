"""
SQLite-backed rule repository.

Implements the RuleRepository Protocol using SQLAlchemy async ORM.
Stores rules in SQLite (or PostgreSQL) for fast concurrent reads.

To switch to PostgreSQL: create a similar repository using asyncpg,
or simply change the DATABASE_URL (same SQLAlchemy models work).
"""

import json
import logging
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.repository.db_models import DeployHistoryRow, MetadataRow, RuleRow

logger = logging.getLogger("policy_engine.sqlite_rule_repository")


class SqliteRuleRepository:
    """Concrete RuleRepository backed by SQLite via SQLAlchemy async."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._sf = session_factory

    # ------------------------------------------------------------------
    # Manifest methods (used by PolicyDeployerUsecase)
    # ------------------------------------------------------------------

    async def get_manifest(self) -> dict:
        """
        Build a manifest dict from the database.

        Returns the same structure as the JSON file:
        {"version": 1, "last_deployed": "...", "rules": [...]}
        """
        async with self._sf() as session:
            # Metadata
            result = await session.execute(select(MetadataRow))
            meta = {row.key: row.value for row in result.scalars().all()}

            # Rules
            rules = await self._query_all_rules(session)

            return {
                "version": int(meta.get("version") or "1"),
                "last_deployed": meta.get("last_deployed"),
                "rules": rules,
            }

    async def save_manifest(self, manifest: dict) -> None:
        """
        Persist manifest metadata (version, last_deployed).

        Rules are managed individually via create/update/delete,
        so only metadata fields are written here.
        """
        async with self._sf() as session:
            if "last_deployed" in manifest:
                await session.merge(
                    MetadataRow(key="last_deployed", value=manifest["last_deployed"])
                )
            if "version" in manifest:
                await session.merge(
                    MetadataRow(key="version", value=str(manifest["version"]))
                )
            await session.commit()

    # ------------------------------------------------------------------
    # Deploy history methods
    # ------------------------------------------------------------------

    async def append_deploy_history(self, entry: dict) -> dict:
        """Insert a new deploy history row with auto-incremented version."""
        async with self._sf() as session:
            # Get next version number
            result = await session.execute(select(func.max(DeployHistoryRow.version)))
            max_version = result.scalar() or 0
            next_version = max_version + 1

            row = DeployHistoryRow(
                version=next_version,
                deployed_at=entry["deployed_at"],
                deployed_by=entry.get("deployed_by", "system"),
                rules_count=entry.get("rules_count", 0),
                roles_json=json.dumps(entry.get("roles", [])),
            )
            session.add(row)
            await session.commit()
            await session.refresh(row)
            return {
                "version": row.version,
                "deployed_at": row.deployed_at,
                "deployed_by": row.deployed_by,
                "rules_count": row.rules_count,
                "roles": row.roles,
            }

    async def get_deploy_history(self, limit: int = 20) -> list[dict]:
        """Return the most recent deploy history entries."""
        async with self._sf() as session:
            result = await session.execute(
                select(DeployHistoryRow)
                .order_by(DeployHistoryRow.id.desc())
                .limit(limit)
            )
            return [
                {
                    "version": row.version,
                    "deployed_at": row.deployed_at,
                    "deployed_by": row.deployed_by,
                    "rules_count": row.rules_count,
                    "roles": row.roles,
                }
                for row in result.scalars().all()
            ]

    # ------------------------------------------------------------------
    # CRUD methods (used by RuleManagementUsecase)
    # ------------------------------------------------------------------

    async def list_rules(self) -> list[dict]:
        """Return all rules as dicts."""
        async with self._sf() as session:
            return await self._query_all_rules(session)

    async def get_rule(self, rule_id: str) -> dict | None:
        """Return a single rule by ID, or None if not found."""
        async with self._sf() as session:
            row = await session.get(RuleRow, rule_id)
            return self._to_dict(row) if row else None

    async def create_rule(self, rule: dict) -> dict:
        """Insert a new rule with auto-generated ID and timestamps."""
        async with self._sf() as session:
            now = datetime.now(timezone.utc).isoformat()
            row = RuleRow(
                id=f"rule-{uuid4().hex[:6]}",
                name=rule["name"],
                description=rule.get("description", ""),
                role=rule["role"],
                institute=rule.get("institute", ""),
                permissions_json=json.dumps(rule.get("permissions", [])),
                enabled=rule.get("enabled", True),
                created_at=now,
                updated_at=now,
            )
            session.add(row)
            await session.commit()
            await session.refresh(row)
            return self._to_dict(row)

    async def update_rule(self, rule_id: str, updates: dict) -> dict | None:
        """Update fields on an existing rule. Returns updated dict or None."""
        async with self._sf() as session:
            row = await session.get(RuleRow, rule_id)
            if not row:
                return None

            for key, value in updates.items():
                if value is None or key in ("id", "created_at"):
                    continue
                if key == "permissions":
                    row.permissions_json = json.dumps(value)
                elif hasattr(row, key):
                    setattr(row, key, value)

            row.updated_at = datetime.now(timezone.utc).isoformat()
            await session.commit()
            await session.refresh(row)
            return self._to_dict(row)

    async def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule by ID. Returns True if deleted."""
        async with self._sf() as session:
            row = await session.get(RuleRow, rule_id)
            if not row:
                return False
            await session.delete(row)
            await session.commit()
            return True

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _query_all_rules(self, session: AsyncSession) -> list[dict]:
        """Fetch all rule rows and convert to dicts."""
        result = await session.execute(select(RuleRow))
        return [self._to_dict(row) for row in result.scalars().all()]

    @staticmethod
    def _to_dict(row: RuleRow) -> dict:
        """Convert a RuleRow to the dict format expected by services."""
        return {
            "id": row.id,
            "name": row.name,
            "description": row.description,
            "role": row.role,
            "institute": row.institute,
            "permissions": row.permissions,  # property does json.loads
            "enabled": row.enabled,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }
