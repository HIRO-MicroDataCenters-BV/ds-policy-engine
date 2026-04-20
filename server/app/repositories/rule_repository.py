"""
Abstract interface (Protocol) for rule persistence.

To switch from JSON file to a database:
  1. Create a new repository implementing this Protocol
  2. Update dependencies.py to wire the new repository
  3. No other code changes needed
"""

from typing import Protocol


class RuleRepository(Protocol):
    """Port interface for rule data storage."""

    async def get_manifest(self) -> dict:
        """Load the full rules manifest."""
        ...

    async def save_manifest(self, manifest: dict) -> None:
        """Persist the full rules manifest."""
        ...

    async def list_rules(self) -> list[dict]:
        """Return all rules from the manifest."""
        ...

    async def get_rule(self, rule_id: str) -> dict | None:
        """Return a single rule by ID, or None if not found."""
        ...

    async def create_rule(self, rule: dict) -> dict:
        """Add a new rule to the manifest and return it."""
        ...

    async def update_rule(self, rule_id: str, updates: dict) -> dict | None:
        """Update a rule by ID. Returns updated rule or None."""
        ...

    async def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule by ID. Returns True if deleted."""
        ...

    async def append_deploy_history(self, entry: dict) -> dict:
        """Insert a new deploy history entry and return the persisted row.

        Return shape includes at minimum ``version`` and ``deployed_at`` —
        PolicyDeployerService.deploy() reads ``result.get("version")``.
        """
        ...

    async def get_deploy_history(self, limit: int = 20) -> list[dict]:
        """Return the most recent deploy history entries."""
        ...
