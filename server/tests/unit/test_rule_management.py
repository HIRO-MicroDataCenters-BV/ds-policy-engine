"""
Unit tests for the rule management service.

Tests CRUD operations, validation, pagination, and error handling
using an in-memory repository (no file I/O).
"""

import pytest

from app.core.exceptions import RuleConflictError, RuleNotFoundError, RuleValidationError
from app.models.rule import PaginationParams, RuleCreate, RuleUpdate
from app.services.rule_management import RuleManagementService


@pytest.fixture
def service(mock_repo_with_seed):
    return RuleManagementService(repository=mock_repo_with_seed)


@pytest.fixture
def empty_service(mock_repo):
    return RuleManagementService(repository=mock_repo)


class TestListRules:
    """Tests for rule listing with pagination, role filtering, enabled filtering, and text search."""

    @pytest.mark.asyncio
    async def test_list_all_rules(self, service):
        """Verify that listing without filters returns all 3 seeded rules."""
        rules, pagination = await service.list_rules(PaginationParams())
        assert len(rules) == 3
        assert pagination.total_items == 3
        assert pagination.total_pages == 1

    @pytest.mark.asyncio
    async def test_pagination_page_size(self, service):
        """Verify that page_size limits the returned rules and pagination metadata is correct."""
        params = PaginationParams(page=1, page_size=2)
        rules, pagination = await service.list_rules(params)
        assert len(rules) == 2
        assert pagination.total_items == 3
        assert pagination.total_pages == 2
        assert pagination.has_next is True
        assert pagination.has_previous is False

    @pytest.mark.asyncio
    async def test_pagination_page_2(self, service):
        """Verify that requesting page 2 returns the remaining rules."""
        params = PaginationParams(page=2, page_size=2)
        rules, pagination = await service.list_rules(params)
        assert len(rules) == 1
        assert pagination.has_next is False
        assert pagination.has_previous is True

    @pytest.mark.asyncio
    async def test_filter_by_role(self, service):
        """Verify that filtering by role returns only rules matching that role."""
        params = PaginationParams(role="catalog_owner")
        rules, _ = await service.list_rules(params)
        assert len(rules) == 1
        assert rules[0]["role"] == "catalog_owner"

    @pytest.mark.asyncio
    async def test_filter_by_enabled(self, service):
        """Verify that filtering by enabled=True returns only enabled rules."""
        params = PaginationParams(enabled=True)
        rules, _ = await service.list_rules(params)
        assert all(r.get("enabled", True) for r in rules)

    @pytest.mark.asyncio
    async def test_search_by_name(self, service):
        """Verify that text search matches rules by name substring."""
        params = PaginationParams(search="owner")
        rules, _ = await service.list_rules(params)
        assert len(rules) == 1
        assert "Owner" in rules[0]["name"]

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self, service):
        """Verify that text search is case-insensitive."""
        params = PaginationParams(search="CREATOR")
        rules, _ = await service.list_rules(params)
        assert len(rules) == 1

    @pytest.mark.asyncio
    async def test_empty_result(self, service):
        """Verify that a search with no matches returns an empty list and zero total."""
        params = PaginationParams(search="nonexistent")
        rules, pagination = await service.list_rules(params)
        assert len(rules) == 0
        assert pagination.total_items == 0


class TestGetRule:
    """Tests for fetching a single rule by ID, including error handling for missing rules."""

    @pytest.mark.asyncio
    async def test_get_existing_rule(self, service):
        """Verify that fetching an existing rule returns the correct data."""
        rule = await service.get_rule("rule-owner-full")
        assert rule["name"] == "Catalog Owner Full Access"
        assert rule["role"] == "catalog_owner"

    @pytest.mark.asyncio
    async def test_get_nonexistent_rule_raises(self, service):
        """Verify that fetching a non-existent rule raises RuleNotFoundError with 404."""
        with pytest.raises(RuleNotFoundError) as exc_info:
            await service.get_rule("rule-nonexistent")
        assert exc_info.value.rule_id == "rule-nonexistent"
        assert exc_info.value.status_code == 404


class TestCreateRule:
    """Tests for rule creation including validation of role format, permission format, duplicate names, and default values."""

    @pytest.mark.asyncio
    async def test_create_valid_rule(self, empty_service):
        """Verify that creating a rule with valid data returns a complete rule dict."""
        data = RuleCreate(
            name="New Rule",
            description="Test rule",
            role="catalog_owner",
            permissions=["catalog:read", "catalog:create"],
        )
        rule = await empty_service.create_rule(data)
        assert rule["name"] == "New Rule"
        assert rule["role"] == "catalog_owner"
        assert rule["id"].startswith("rule-")
        assert "created_at" in rule
        assert "updated_at" in rule

    @pytest.mark.asyncio
    async def test_create_rule_invalid_role_format_raises(self, empty_service):
        """Role must be lowercase, start with letter, 2-64 chars."""
        data = RuleCreate(name="Bad", role="123Bad", permissions=["catalog:read"])
        with pytest.raises(RuleValidationError) as exc_info:
            await empty_service.create_rule(data)
        assert exc_info.value.field == "role"
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_rule_custom_role_succeeds(self, empty_service):
        """Custom roles (not in seed enums) should be accepted if format is valid."""
        data = RuleCreate(
            name="Custom Role Rule", role="data_steward", permissions=["catalog:read"]
        )
        rule = await empty_service.create_rule(data)
        assert rule["role"] == "data_steward"

    @pytest.mark.asyncio
    async def test_create_rule_invalid_permission_format_raises(self, empty_service):
        """Permissions must follow resource:action format."""
        data = RuleCreate(name="Bad", role="catalog_owner", permissions=["notvalid"])
        with pytest.raises(RuleValidationError) as exc_info:
            await empty_service.create_rule(data)
        assert exc_info.value.field == "permissions"

    @pytest.mark.asyncio
    async def test_create_rule_custom_permission_succeeds(self, empty_service):
        """Custom permissions (not in seed enums) should be accepted if format is valid."""
        data = RuleCreate(
            name="Custom Perm Rule", role="catalog_owner", permissions=["data-export:execute"]
        )
        rule = await empty_service.create_rule(data)
        assert "data-export:execute" in rule["permissions"]

    @pytest.mark.asyncio
    async def test_create_duplicate_name_raises(self, service):
        """Verify that creating a rule with a duplicate name raises RuleConflictError."""
        data = RuleCreate(
            name="Catalog Owner Full Access",
            role="catalog_owner",
            permissions=["catalog:read"],
        )
        with pytest.raises(RuleConflictError) as exc_info:
            await service.create_rule(data)
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_create_rule_defaults_enabled(self, empty_service):
        """Verify that a newly created rule defaults to enabled=True."""
        data = RuleCreate(name="Test", role="catalog_consumer", permissions=["catalog:read"])
        rule = await empty_service.create_rule(data)
        assert rule["enabled"] is True


class TestUpdateRule:
    """Tests for partial rule updates including name, permissions, and validation of invalid inputs."""

    @pytest.mark.asyncio
    async def test_update_name(self, service):
        """Verify that updating a rule's name succeeds without changing other fields."""
        data = RuleUpdate(name="Updated Name")
        rule = await service.update_rule("rule-owner-full", data)
        assert rule["name"] == "Updated Name"
        assert rule["role"] == "catalog_owner"  # unchanged

    @pytest.mark.asyncio
    async def test_update_permissions(self, service):
        """Verify that a rule's permissions can be replaced via update."""
        data = RuleUpdate(permissions=["catalog:read"])
        rule = await service.update_rule("rule-owner-full", data)
        assert rule["permissions"] == ["catalog:read"]

    @pytest.mark.asyncio
    async def test_update_nonexistent_raises(self, service):
        """Verify that updating a non-existent rule raises RuleNotFoundError."""
        data = RuleUpdate(name="Nope")
        with pytest.raises(RuleNotFoundError):
            await service.update_rule("rule-nonexistent", data)

    @pytest.mark.asyncio
    async def test_update_invalid_role_format_raises(self, service):
        """Format-invalid role should be rejected."""
        data = RuleUpdate(role="X")
        with pytest.raises(RuleValidationError):
            await service.update_rule("rule-owner-full", data)

    @pytest.mark.asyncio
    async def test_update_invalid_permission_format_raises(self, service):
        """Format-invalid permission should be rejected."""
        data = RuleUpdate(permissions=["NOCOLON"])
        with pytest.raises(RuleValidationError):
            await service.update_rule("rule-owner-full", data)


class TestDeleteRule:
    """Tests for rule deletion including removal verification and error handling for missing rules."""

    @pytest.mark.asyncio
    async def test_delete_existing_rule(self, service):
        """Verify that deleting an existing rule removes it from the repository."""
        await service.delete_rule("rule-owner-full")
        with pytest.raises(RuleNotFoundError):
            await service.get_rule("rule-owner-full")

    @pytest.mark.asyncio
    async def test_delete_nonexistent_raises(self, service):
        """Verify that deleting a non-existent rule raises RuleNotFoundError."""
        with pytest.raises(RuleNotFoundError):
            await service.delete_rule("rule-nonexistent")


class TestToggleRule:
    """Tests for toggling the enabled state of a rule, including double-toggle and missing rule errors."""

    @pytest.mark.asyncio
    async def test_toggle_disables_enabled_rule(self, service):
        """Verify that toggling an enabled rule sets enabled to False."""
        rule = await service.toggle_rule("rule-owner-full")
        assert rule["enabled"] is False

    @pytest.mark.asyncio
    async def test_toggle_twice_re_enables(self, service):
        """Verify that toggling a rule twice restores it to enabled."""
        await service.toggle_rule("rule-owner-full")
        rule = await service.toggle_rule("rule-owner-full")
        assert rule["enabled"] is True

    @pytest.mark.asyncio
    async def test_toggle_nonexistent_raises(self, service):
        """Verify that toggling a non-existent rule raises RuleNotFoundError."""
        with pytest.raises(RuleNotFoundError):
            await service.toggle_rule("rule-nonexistent")
