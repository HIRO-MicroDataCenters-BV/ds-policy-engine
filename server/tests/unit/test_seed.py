"""
Unit tests for the database seed logic.

Tests that seed_from_json correctly populates an empty database
from a JSON file and skips seeding when data already exists.
"""

import json
import pathlib

import pytest
from sqlalchemy import select

from app.db.models import MetadataRow, RuleRow
from app.db.seed import seed_from_json
from app.repositories.sqlite_rule_repository import SqliteRuleRepository


class TestSeedFromJson:
    """Tests for the seed_from_json function."""

    @pytest.mark.asyncio
    async def test_seeds_empty_database(self, db_session_factory, seed_rules_file):
        """Verify that seeding an empty database inserts all 3 rules."""
        count = await seed_from_json(db_session_factory, seed_rules_file)
        assert count == 3

    @pytest.mark.asyncio
    async def test_seeded_rules_are_queryable(self, db_session_factory, seed_rules_file):
        """Verify that seeded rules can be queried directly from the database."""
        await seed_from_json(db_session_factory, seed_rules_file)

        async with db_session_factory() as session:
            result = await session.execute(select(RuleRow))
            rules = result.scalars().all()
            assert len(rules) == 3

    @pytest.mark.asyncio
    async def test_seeded_rules_have_correct_ids(self, db_session_factory, seed_rules_file):
        """Verify that seeded rules retain their original IDs from the JSON file."""
        await seed_from_json(db_session_factory, seed_rules_file)

        async with db_session_factory() as session:
            result = await session.execute(select(RuleRow))
            ids = {row.id for row in result.scalars().all()}
            assert ids == {"rule-owner-full", "rule-creator-local", "rule-consumer-read"}

    @pytest.mark.asyncio
    async def test_seeded_rules_have_permissions(self, db_session_factory, seed_rules_file):
        """Verify that seeded rules have the correct permissions stored."""
        await seed_from_json(db_session_factory, seed_rules_file)

        async with db_session_factory() as session:
            row = await session.get(RuleRow, "rule-owner-full")
            assert row is not None
            perms = row.permissions
            assert "catalog:read" in perms
            assert len(perms) == 6

    @pytest.mark.asyncio
    async def test_seeds_metadata(self, db_session_factory, seed_rules_file):
        """Verify that version and last_deployed metadata are seeded correctly."""
        await seed_from_json(db_session_factory, seed_rules_file)

        async with db_session_factory() as session:
            result = await session.execute(select(MetadataRow))
            meta = {row.key: row.value for row in result.scalars().all()}
            assert meta["version"] == "1"
            assert meta["last_deployed"] == "2026-04-02T00:00:00Z"

    @pytest.mark.asyncio
    async def test_skips_if_db_has_data(self, db_session_factory, seed_rules_file):
        """Verify that seeding is skipped when the database already has rules."""
        # First seed
        first_count = await seed_from_json(db_session_factory, seed_rules_file)
        assert first_count == 3

        # Second seed — should skip
        second_count = await seed_from_json(db_session_factory, seed_rules_file)
        assert second_count == 0

        # Verify no duplicates
        async with db_session_factory() as session:
            result = await session.execute(select(RuleRow))
            assert len(result.scalars().all()) == 3

    @pytest.mark.asyncio
    async def test_returns_zero_for_missing_file(self, db_session_factory):
        """Verify that a missing seed file results in zero rules inserted."""
        count = await seed_from_json(db_session_factory, "/nonexistent/path.json")
        assert count == 0

    @pytest.mark.asyncio
    async def test_returns_zero_for_empty_rules(self, db_session_factory, temp_policies_dir):
        """Verify that a seed file with an empty rules array inserts nothing."""
        # Write a seed file with no rules
        path = pathlib.Path(temp_policies_dir) / "empty.json"
        path.write_text(json.dumps({"version": 1, "rules": []}), encoding="utf-8")

        count = await seed_from_json(db_session_factory, str(path))
        assert count == 0

    @pytest.mark.asyncio
    async def test_seeded_data_accessible_via_repository(
        self, db_session_factory, seed_rules_file
    ):
        """Verify seed data works through the repository layer."""
        await seed_from_json(db_session_factory, seed_rules_file)

        repo = SqliteRuleRepository(db_session_factory)
        rules = await repo.list_rules()
        assert len(rules) == 3

        owner = await repo.get_rule("rule-owner-full")
        assert owner is not None
        assert owner["role"] == "catalog_owner"
        assert "catalog:read" in owner["permissions"]
