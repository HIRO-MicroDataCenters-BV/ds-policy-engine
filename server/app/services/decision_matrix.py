"""
Decision matrix service.

Builds a live matrix showing permissions for every role
by querying the policy engine.

The matrix is **dynamic** — it discovers roles and permissions from
the rule repository rather than relying on hardcoded enums, so custom
roles/permissions added via the Policy Builder are automatically included.
"""

import logging

from app.adapters.policy_engine import PolicyEngine
from app.repositories.rule_repository import RuleRepository

logger = logging.getLogger("policy_engine.decision_matrix")


class DecisionMatrixService:
    """Generates a live decision matrix by querying the engine for each role."""

    def __init__(self, engine: PolicyEngine, repository: RuleRepository):
        self._engine = engine
        self._repo = repository

    async def build_matrix(self) -> dict:
        """
        Query the engine for every known role and build the full matrix.

        Roles and permissions are discovered dynamically from the rule
        repository so that custom values appear automatically.

        Returns:
            Dict with "matrix" list, "roles" list, and "permissions" list.
        """
        # Discover roles and permissions from actual rules
        rules = await self._repo.list_rules()
        roles = sorted({r.get("role") for r in rules if r.get("role")})
        all_perms = set()
        for r in rules:
            all_perms.update(r.get("permissions", []))
        all_perms = sorted(all_perms)

        # Build role -> institute mapping from rules so we query OPA with the
        # correct institute for each role (a role may appear under multiple
        # institutes, so we collect all unique (role, institute) pairs).
        role_institute_pairs = []
        seen_pairs = set()
        for r in rules:
            role = r.get("role", "")
            inst = r.get("institute", "")
            if role and (role, inst) not in seen_pairs:
                seen_pairs.add((role, inst))
                role_institute_pairs.append((role, inst, r.get("name", "")))

        logger.debug(
            "Building matrix: %d role-institute pairs × %d permissions",
            len(role_institute_pairs),
            len(all_perms),
        )

        matrix = []
        for role, institute, rule_name in role_institute_pairs:
            input_data = {
                "name": f"matrix-{role}",
                "email": f"{role}@test.local",
                "role": role,
                "institute": institute,
            }

            try:
                result = await self._engine.evaluate(input_data)
                permissions = result.get("permissions", [])
            except Exception:
                logger.warning(
                    "Matrix evaluation failed for role=%s institute=%s", role, institute
                )
                permissions = []

            entry = {"role": role, "institute": institute, "permissions": permissions}
            if rule_name:
                entry["rule_name"] = rule_name
            # Add a boolean flag for each known permission
            for perm in all_perms:
                key = perm.replace(":", "_").replace("-", "_")
                entry[key] = perm in permissions
            matrix.append(entry)

        return {
            "matrix": matrix,
            "roles": roles,
            "permissions": all_perms,
        }
