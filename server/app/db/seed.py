"""
Database seed logic.

Loads initial rules from seed_rules.json into an empty database.
Only runs on first startup — skips if the database already has data.
"""

import json
import logging
import pathlib
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import settings
from app.core.repository.db_models import MetadataRow, RuleRow

logger = logging.getLogger("policy_engine.seed")


async def seed_from_json(
    session_factory: async_sessionmaker[AsyncSession],
    seed_path: str,
) -> int:
    """
    Load seed rules from a JSON file if the database is empty.

    Args:
        session_factory: SQLAlchemy async session factory.
        seed_path: Path to the seed_rules.json file.

    Returns:
        Number of rules seeded (0 if DB already has data).
    """
    # Check if DB already has rules
    async with session_factory() as session:
        result = await session.execute(select(RuleRow).limit(1))
        if result.scalars().first():
            return 0

    # Load seed file
    path = pathlib.Path(seed_path)
    if not path.exists():
        logger.warning("Seed file not found: %s", seed_path)
        return 0

    manifest = json.loads(path.read_text(encoding="utf-8"))
    rules = manifest.get("rules", [])
    if not rules:
        logger.info("Seed file has no rules")
        return 0

    # Insert seed data
    async with session_factory() as session:
        now = datetime.now(timezone.utc).isoformat()
        for rule in rules:
            row = RuleRow(
                id=rule["id"],
                name=rule["name"],
                description=rule.get("description", ""),
                role=rule["role"],
                institute=rule.get("institute", "") or settings.node_name,
                permissions_json=json.dumps(rule.get("permissions", [])),
                enabled=rule.get("enabled", True),
                created_at=rule.get("created_at", now),
                updated_at=rule.get("updated_at", now),
            )
            session.add(row)

        # Seed metadata
        await session.merge(
            MetadataRow(key="version", value=str(manifest.get("version", 1)))
        )
        if manifest.get("last_deployed"):
            await session.merge(
                MetadataRow(key="last_deployed", value=manifest["last_deployed"])
            )

        await session.commit()

    logger.info("Seeded %d rules from %s", len(rules), seed_path)
    return len(rules)
