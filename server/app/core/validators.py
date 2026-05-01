"""
Business validators.

Format-level checks on role and permission identifiers used by the rule
CRUD use cases. Kept independent of Pydantic so the same rules apply
whether the input came from the HTTP layer or a bulk import path.
"""

import logging
import re

from app.core.exceptions import RuleValidationError

logger = logging.getLogger("policy_engine.validators")


_ROLE_PATTERN = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
_PERM_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*:[a-z][a-z0-9_-]*$")


def validate_role(role: str) -> None:
    """Validate a role identifier format.

    Roles must be lowercase, start with a letter, contain only
    letters/digits/underscores, and be 2-64 characters long.
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


def validate_permissions(permissions: list[str]) -> None:
    """Validate permission identifier formats.

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
