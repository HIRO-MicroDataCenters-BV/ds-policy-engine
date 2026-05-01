"""
Domain constants — default roles, permissions, and mappings.

These serve as the initial seed vocabulary.  At runtime, the system
reads actual roles and permissions from the rule repository so that
users can create custom roles/permissions via the Policy Builder UI.
"""

from enum import Enum


class Role(str, Enum):
    """Built-in roles shipped with the seed rules."""

    CATALOG_OWNER = "catalog_owner"
    CATALOG_CREATOR = "catalog_creator"
    CATALOG_CONSUMER = "catalog_consumer"


class Permission(str, Enum):
    """Built-in permissions shipped with the seed rules."""

    CATALOG_READ = "catalog:read"
    CATALOG_CREATE = "catalog:create"
    CATALOG_UPDATE = "catalog:update"
    CATALOG_DELETE = "catalog:delete"
    DECENTRALIZED_SEARCH = "decentralized-search:execute"
    FEDERATED_LEARNING = "federated-learning:execute"


# Default permission matrix — used by seed rules
DEFAULT_ROLE_PERMISSIONS: dict[str, list[str]] = {
    Role.CATALOG_OWNER: [p.value for p in Permission],
    Role.CATALOG_CREATOR: [
        Permission.CATALOG_READ.value,
        Permission.CATALOG_CREATE.value,
        Permission.CATALOG_UPDATE.value,
        Permission.CATALOG_DELETE.value,
    ],
    Role.CATALOG_CONSUMER: [
        Permission.CATALOG_READ.value,
    ],
}

# Seed values — used as fallback when no rules exist yet
SEED_ROLES = [r.value for r in Role]
SEED_PERMISSIONS = [p.value for p in Permission]
