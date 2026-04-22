"""
Unit tests for the SQLite rule repository.

Tests all CRUD operations and manifest methods against a real
in-memory SQLite database (no mocks).
"""

import pytest

from app.core.repository.sqlite_rule_repository import SqliteRuleRepository


@pytest.fixture
def repo(db_session_factory):
    return SqliteRuleRepository(db_session_factory)


@pytest.fixture
async def seeded_repo(repo):
    """Repository with 3 seed rules pre-inserted."""
    await repo.create_rule(
        {
            "name": "Owner Rule",
            "role": "catalog_owner",
            "permissions": ["catalog:read", "catalog:create"],
        }
    )
    await repo.create_rule(
        {
            "name": "Creator Rule",
            "role": "catalog_creator",
            "permissions": ["catalog:read", "catalog:create"],
        }
    )
    await repo.create_rule(
        {
            "name": "Consumer Rule",
            "role": "catalog_consumer",
            "permissions": ["catalog:read"],
        }
    )
    return repo


class TestCreateRule:
    """Tests for inserting rules into SQLite, including auto-generated IDs, timestamps, default values, and multiple inserts."""

    @pytest.mark.asyncio
    async def test_create_rule_returns_dict(self, repo):
        """Verify that creating a rule returns a dict with the correct fields."""
        rule = await repo.create_rule(
            {
                "name": "Test Rule",
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
            }
        )
        assert isinstance(rule, dict)
        assert rule["name"] == "Test Rule"
        assert rule["role"] == "catalog_owner"
        assert rule["permissions"] == ["catalog:read"]

    @pytest.mark.asyncio
    async def test_create_rule_generates_id(self, repo):
        """Verify that created rules get an auto-generated ID starting with 'rule-'."""
        rule = await repo.create_rule(
            {
                "name": "ID Test",
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
            }
        )
        assert rule["id"].startswith("rule-")
        assert len(rule["id"]) == 11  # "rule-" + 6 hex chars

    @pytest.mark.asyncio
    async def test_create_rule_generates_timestamps(self, repo):
        """Verify that created_at and updated_at are set and equal on creation."""
        rule = await repo.create_rule(
            {
                "name": "Timestamp Test",
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
            }
        )
        assert "created_at" in rule
        assert "updated_at" in rule
        assert rule["created_at"] == rule["updated_at"]

    @pytest.mark.asyncio
    async def test_create_rule_defaults_enabled(self, repo):
        """Verify that a rule defaults to enabled=True when not specified."""
        rule = await repo.create_rule(
            {
                "name": "Enabled Test",
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
            }
        )
        assert rule["enabled"] is True

    @pytest.mark.asyncio
    async def test_create_rule_explicit_disabled(self, repo):
        """Verify that passing enabled=False is preserved on creation."""
        rule = await repo.create_rule(
            {
                "name": "Disabled Test",
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
                "enabled": False,
            }
        )
        assert rule["enabled"] is False

    @pytest.mark.asyncio
    async def test_create_rule_with_description(self, repo):
        """Verify that an optional description field is stored correctly."""
        rule = await repo.create_rule(
            {
                "name": "Desc Test",
                "description": "A detailed description",
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
            }
        )
        assert rule["description"] == "A detailed description"

    @pytest.mark.asyncio
    async def test_create_rule_empty_permissions(self, repo):
        """Verify that a rule can be created with an empty permissions list."""
        rule = await repo.create_rule(
            {
                "name": "Empty Perms",
                "role": "catalog_owner",
                "permissions": [],
            }
        )
        assert rule["permissions"] == []

    @pytest.mark.asyncio
    async def test_create_multiple_rules(self, repo):
        """Verify that multiple rules can be inserted and all are listed."""
        for i in range(5):
            await repo.create_rule(
                {
                    "name": f"Rule {i}",
                    "role": "catalog_owner",
                    "permissions": ["catalog:read"],
                }
            )
        rules = await repo.list_rules()
        assert len(rules) == 5


class TestGetRule:
    """Tests for fetching a single rule by ID, including field completeness and missing rule handling."""

    @pytest.mark.asyncio
    async def test_get_existing_rule(self, repo):
        """Verify that a previously created rule can be fetched by its ID."""
        created = await repo.create_rule(
            {
                "name": "Fetch Me",
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
            }
        )
        fetched = await repo.get_rule(created["id"])
        assert fetched is not None
        assert fetched["id"] == created["id"]
        assert fetched["name"] == "Fetch Me"

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_none(self, repo):
        """Verify that fetching a non-existent rule ID returns None."""
        result = await repo.get_rule("rule-nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_rule_has_all_fields(self, repo):
        """Verify that a fetched rule contains all expected keys."""
        created = await repo.create_rule(
            {
                "name": "Full Fields",
                "description": "Test desc",
                "role": "catalog_consumer",
                "permissions": ["catalog:read", "catalog:create"],
            }
        )
        fetched = await repo.get_rule(created["id"])
        expected_keys = {
            "id",
            "name",
            "description",
            "role",
            "institute",
            "permissions",
            "enabled",
            "created_at",
            "updated_at",
        }
        assert set(fetched.keys()) == expected_keys


class TestListRules:
    """Tests for listing all rules from SQLite, including empty DB, data types, and permissions deserialization."""

    @pytest.mark.asyncio
    async def test_list_empty_db(self, repo):
        """Verify that listing rules on an empty database returns an empty list."""
        rules = await repo.list_rules()
        assert rules == []

    @pytest.mark.asyncio
    async def test_list_returns_all_rules(self, seeded_repo):
        """Verify that list_rules returns all 3 seeded rules."""
        rules = await seeded_repo.list_rules()
        assert len(rules) == 3

    @pytest.mark.asyncio
    async def test_list_rules_are_dicts(self, seeded_repo):
        """Verify that each listed rule is a dict with id and permissions keys."""
        rules = await seeded_repo.list_rules()
        for rule in rules:
            assert isinstance(rule, dict)
            assert "id" in rule
            assert "permissions" in rule

    @pytest.mark.asyncio
    async def test_list_permissions_are_lists(self, seeded_repo):
        """Verify that the permissions field is deserialized as a Python list."""
        rules = await seeded_repo.list_rules()
        for rule in rules:
            assert isinstance(rule["permissions"], list)


class TestUpdateRule:
    """Tests for updating existing rules including partial updates, timestamp behavior, and ID immutability."""

    @pytest.mark.asyncio
    async def test_update_name(self, repo):
        """Verify that updating a rule's name changes it while preserving other fields."""
        created = await repo.create_rule(
            {
                "name": "Original",
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
            }
        )
        updated = await repo.update_rule(created["id"], {"name": "Renamed"})
        assert updated["name"] == "Renamed"
        assert updated["role"] == "catalog_owner"  # unchanged

    @pytest.mark.asyncio
    async def test_update_permissions(self, repo):
        """Verify that a rule's permissions list can be updated."""
        created = await repo.create_rule(
            {
                "name": "Perm Test",
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
            }
        )
        updated = await repo.update_rule(
            created["id"], {"permissions": ["catalog:read", "catalog:create"]}
        )
        assert updated["permissions"] == ["catalog:read", "catalog:create"]

    @pytest.mark.asyncio
    async def test_update_enabled_state(self, repo):
        """Verify that the enabled flag can be toggled via update."""
        created = await repo.create_rule(
            {
                "name": "Toggle Test",
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
            }
        )
        updated = await repo.update_rule(created["id"], {"enabled": False})
        assert updated["enabled"] is False

    @pytest.mark.asyncio
    async def test_update_preserves_created_at(self, repo):
        """Verify that updating a rule does not change its created_at timestamp."""
        created = await repo.create_rule(
            {
                "name": "Timestamp Preserve",
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
            }
        )
        updated = await repo.update_rule(created["id"], {"name": "New Name"})
        assert updated["created_at"] == created["created_at"]

    @pytest.mark.asyncio
    async def test_update_changes_updated_at(self, repo):
        """Verify that updating a rule advances its updated_at timestamp."""
        created = await repo.create_rule(
            {
                "name": "Time Change",
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
            }
        )
        updated = await repo.update_rule(created["id"], {"name": "Changed"})
        # updated_at should be >= created_at (same second is ok)
        assert updated["updated_at"] >= created["updated_at"]

    @pytest.mark.asyncio
    async def test_update_nonexistent_returns_none(self, repo):
        """Verify that updating a non-existent rule returns None."""
        result = await repo.update_rule("rule-nonexistent", {"name": "X"})
        assert result is None

    @pytest.mark.asyncio
    async def test_update_ignores_id_change(self, repo):
        """Verify that attempting to change a rule's ID via update is ignored."""
        created = await repo.create_rule(
            {
                "name": "ID Protect",
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
            }
        )
        updated = await repo.update_rule(created["id"], {"id": "rule-hacked"})
        assert updated["id"] == created["id"]


class TestDeleteRule:
    """Tests for deleting rules from SQLite, including verification of removal and count reduction."""

    @pytest.mark.asyncio
    async def test_delete_existing_rule(self, repo):
        """Verify that deleting an existing rule returns True and removes it."""
        created = await repo.create_rule(
            {
                "name": "Delete Me",
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
            }
        )
        result = await repo.delete_rule(created["id"])
        assert result is True
        assert await repo.get_rule(created["id"]) is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_returns_false(self, repo):
        """Verify that deleting a non-existent rule returns False."""
        result = await repo.delete_rule("rule-nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_reduces_count(self, seeded_repo):
        """Verify that deleting a rule decreases the total rule count by one."""
        rules_before = await seeded_repo.list_rules()
        await seeded_repo.delete_rule(rules_before[0]["id"])
        rules_after = await seeded_repo.list_rules()
        assert len(rules_after) == len(rules_before) - 1


class TestManifest:
    """Tests for manifest get/save operations including default values, version updates, and consistency with list_rules."""

    @pytest.mark.asyncio
    async def test_get_manifest_empty_db(self, repo):
        """Verify that an empty DB returns a default manifest with version 1 and no rules."""
        manifest = await repo.get_manifest()
        assert manifest["version"] == 1
        assert manifest["last_deployed"] is None
        assert manifest["rules"] == []

    @pytest.mark.asyncio
    async def test_get_manifest_with_rules(self, seeded_repo):
        """Verify that the manifest includes all seeded rules."""
        manifest = await seeded_repo.get_manifest()
        assert len(manifest["rules"]) == 3
        assert "version" in manifest

    @pytest.mark.asyncio
    async def test_save_manifest_updates_last_deployed(self, repo):
        """Verify that saving a manifest persists the last_deployed timestamp."""
        await repo.save_manifest(
            {
                "version": 1,
                "last_deployed": "2026-04-02T12:00:00Z",
            }
        )
        manifest = await repo.get_manifest()
        assert manifest["last_deployed"] == "2026-04-02T12:00:00Z"

    @pytest.mark.asyncio
    async def test_save_manifest_updates_version(self, repo):
        """Verify that saving a manifest persists a new version number."""
        await repo.save_manifest({"version": 2})
        manifest = await repo.get_manifest()
        assert manifest["version"] == 2

    @pytest.mark.asyncio
    async def test_manifest_rules_match_list_rules(self, seeded_repo):
        """Verify that manifest rules and list_rules return the same rule IDs."""
        manifest = await seeded_repo.get_manifest()
        rules = await seeded_repo.list_rules()
        assert len(manifest["rules"]) == len(rules)
        manifest_ids = {r["id"] for r in manifest["rules"]}
        list_ids = {r["id"] for r in rules}
        assert manifest_ids == list_ids
