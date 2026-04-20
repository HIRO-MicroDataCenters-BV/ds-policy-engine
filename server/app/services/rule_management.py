"""
Rule management service.

Business logic for CRUD operations on policy rules.
Handles validation, pagination, and delegates persistence to the repository.

Roles and permissions are **dynamic** — users can create custom values
via the Policy Builder.  Validation enforces format (non-empty, valid
characters) rather than membership in a fixed enum.
"""

import logging
import math
import re

from app.core.exceptions import (
    RuleConflictError,
    RuleNotFoundError,
    RuleValidationError,
)
from app.models.rule import PaginationMeta, PaginationParams, RuleCreate, RuleUpdate
from app.repositories.rule_repository import RuleRepository

logger = logging.getLogger("policy_engine.rule_management")

# Regex for valid role/permission identifiers
_ROLE_PATTERN = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
_PERM_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*:[a-z][a-z0-9_-]*$")


class RuleManagementService:
    """Manages policy rules with validation and pagination."""

    def __init__(self, repository: RuleRepository):
        self._repo = repository

    def _validate_role(self, role: str) -> None:
        """
        Validate a role identifier format.

        Roles must be lowercase, start with a letter, contain only
        letters, digits, and underscores, and be 2-64 characters long.
        """
        if not _ROLE_PATTERN.match(role):
            logger.warning("Invalid role format: '%s'", role)
            raise RuleValidationError(
                message=(
                    f"Invalid role '{role}'. Roles must be lowercase, start with a letter, "
                    "contain only letters/digits/underscores, and be 2-64 characters long. "
                    "Example: catalog_owner, data_steward"
                ),
                field="role",
                value=role,
            )

    def _validate_permissions(self, permissions: list[str]) -> None:
        """
        Validate permission identifier formats.

        Permissions must follow the ``resource:action`` pattern using
        lowercase letters, digits, hyphens, and underscores.
        """
        invalid = [p for p in permissions if not _PERM_PATTERN.match(p)]
        if invalid:
            logger.warning("Invalid permission format: %s", invalid)
            raise RuleValidationError(
                message=(
                    f"Invalid permission format: {', '.join(invalid)}. "
                    "Permissions must follow 'resource:action' pattern using "
                    "lowercase letters, digits, hyphens, underscores. "
                    "Example: catalog:read, decentralized-search:execute"
                ),
                field="permissions",
                value=", ".join(invalid),
            )

    async def list_rules(
        self, params: PaginationParams
    ) -> tuple[list[dict], PaginationMeta]:
        """List rules with pagination, filtering, and sorting."""
        all_rules = await self._repo.list_rules()

        # Filter
        if params.role:
            all_rules = [r for r in all_rules if r.get("role") == params.role]
        if params.enabled is not None:
            all_rules = [
                r for r in all_rules if r.get("enabled", True) == params.enabled
            ]
        if params.search:
            q = params.search.lower()
            all_rules = [r for r in all_rules if q in r.get("name", "").lower()]

        # Sort
        reverse = params.sort_order == "desc"
        all_rules.sort(key=lambda r: r.get(params.sort_by, ""), reverse=reverse)

        # Paginate
        total_items = len(all_rules)
        total_pages = max(1, math.ceil(total_items / params.page_size))
        start = (params.page - 1) * params.page_size
        end = start + params.page_size
        page_rules = all_rules[start:end]

        pagination = PaginationMeta(
            page=params.page,
            page_size=params.page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_previous=params.page > 1,
        )

        return page_rules, pagination

    async def get_rule(self, rule_id: str) -> dict:
        """Get a single rule by ID."""
        rule = await self._repo.get_rule(rule_id)
        if not rule:
            raise RuleNotFoundError(rule_id)
        return rule

    async def create_rule(self, data: RuleCreate) -> dict:
        """Create a new rule with validation."""
        self._validate_role(data.role)
        self._validate_permissions(data.permissions)

        # Check for duplicate name
        existing = await self._repo.list_rules()
        for r in existing:
            if r.get("name", "").lower() == data.name.lower():
                raise RuleConflictError(
                    message=f"A rule named '{data.name}' already exists",
                    existing_rule_id=r["id"],
                )

        rule_data = data.model_dump()
        rule = await self._repo.create_rule(rule_data)
        logger.info("Created rule '%s' (%s)", rule["name"], rule["id"])
        return rule

    async def update_rule(self, rule_id: str, data: RuleUpdate) -> dict:
        """Update an existing rule."""
        updates = data.model_dump(exclude_none=True)

        if "role" in updates:
            self._validate_role(updates["role"])
        if "permissions" in updates:
            self._validate_permissions(updates["permissions"])

        result = await self._repo.update_rule(rule_id, updates)
        if not result:
            raise RuleNotFoundError(rule_id)
        logger.info("Updated rule '%s'", rule_id)
        return result

    async def delete_rule(self, rule_id: str) -> None:
        """Delete a rule by ID."""
        deleted = await self._repo.delete_rule(rule_id)
        if not deleted:
            raise RuleNotFoundError(rule_id)
        logger.info("Deleted rule '%s'", rule_id)

    async def toggle_rule(self, rule_id: str) -> dict:
        """Toggle a rule's enabled state."""
        rule = await self._repo.get_rule(rule_id)
        if not rule:
            raise RuleNotFoundError(rule_id)
        new_state = not rule.get("enabled", True)
        result = await self._repo.update_rule(rule_id, {"enabled": new_state})
        # Rule was there when we read it but is gone now — treat as not found
        # rather than propagating None and crashing callers that expect a dict.
        if result is None:
            raise RuleNotFoundError(rule_id)
        logger.info("Toggled rule '%s' -> enabled=%s", rule_id, new_state)
        return result

    async def get_known_roles(self) -> list[str]:
        """
        Collect all unique roles currently used across rules.

        Returns a deduplicated, sorted list of role strings.
        """
        rules = await self._repo.list_rules()
        roles = sorted({r.get("role") for r in rules if r.get("role")})
        return roles

    async def get_known_permissions(self) -> list[str]:
        """
        Collect all unique permissions currently used across rules.

        Returns a deduplicated, sorted list of permission strings.
        """
        rules = await self._repo.list_rules()
        perms = set()
        for r in rules:
            perms.update(r.get("permissions", []))
        return sorted(perms)

    async def get_meta(self) -> dict:
        """
        Collect all unique roles, institutes, and permissions from rules.

        Returns a single dict with deduplicated, sorted lists for each.
        """
        rules = await self._repo.list_rules()
        roles = sorted({r.get("role") for r in rules if r.get("role")})
        institutes = sorted({r.get("institute") for r in rules if r.get("institute")})
        perms = set()
        # Collect unique (role, institute) pairs across ALL rules (enabled or
        # disabled) — the Tester dropdowns need to show disabled scenarios so
        # users can preview what enabling the rule would do. If the UI wants
        # only enabled scenarios later, add an explicit filter here.
        role_institute_pairs = []
        seen_pairs = set()
        for r in rules:
            perms.update(r.get("permissions", []))
            role = r.get("role", "")
            inst = r.get("institute", "")
            if role and inst and (role, inst) not in seen_pairs:
                seen_pairs.add((role, inst))
                role_institute_pairs.append(
                    {"role": role, "institute": inst, "name": r.get("name", "")}
                )
        return {
            "roles": roles,
            "institutes": institutes,
            "permissions": sorted(perms),
            "rule_scenarios": sorted(role_institute_pairs, key=lambda x: x["role"]),
        }
