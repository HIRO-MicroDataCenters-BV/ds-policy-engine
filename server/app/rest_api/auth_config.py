"""Permission map used when ds-auth is enabled on this service.

Design:
  * Everything that mutates rules or executes an operational action requires
    ``rules:admin``.
  * ``POST /api/v1/policies/evaluate`` is deliberately open — services that
    use ds-auth call it unauthenticated to resolve their callers' permissions,
    including ds-auth running inside *this* process.
  * Health, docs, and OpenAPI stay public.

Policy engine route rules (regex, first match wins):
"""

from __future__ import annotations

ADMIN_PERMISSION = "rules:admin"

# (METHOD, path regex, required permission)
PERMISSION_MAP: list[tuple[str, str, str]] = [
    # Rules — CRUD + import/export + metadata
    ("GET", r"^/api/v1/rules/?$", ADMIN_PERMISSION),
    ("POST", r"^/api/v1/rules/?$", ADMIN_PERMISSION),
    ("GET", r"^/api/v1/rules/[^/]+/?$", ADMIN_PERMISSION),
    ("PUT", r"^/api/v1/rules/[^/]+/?$", ADMIN_PERMISSION),
    ("DELETE", r"^/api/v1/rules/[^/]+/?$", ADMIN_PERMISSION),
    ("PATCH", r"^/api/v1/rules/[^/]+/toggle/?$", ADMIN_PERMISSION),
    ("GET", r"^/api/v1/rules/meta/?$", ADMIN_PERMISSION),
    ("GET", r"^/api/v1/rules/meta/.+$", ADMIN_PERMISSION),
    ("GET", r"^/api/v1/rules/export/.+$", ADMIN_PERMISSION),
    ("POST", r"^/api/v1/rules/import/.+$", ADMIN_PERMISSION),
    # Policies — deploy / preview / history / overview
    ("POST", r"^/api/v1/policies/deploy/?$", ADMIN_PERMISSION),
    ("POST", r"^/api/v1/policies/preview/?$", ADMIN_PERMISSION),
    ("GET", r"^/api/v1/policies/deploy-history/?$", ADMIN_PERMISSION),
    ("GET", r"^/api/v1/policies/overview/?$", ADMIN_PERMISSION),
    # OPA passthrough — admin only
    ("GET", r"^/api/v1/opa/.+$", ADMIN_PERMISSION),
    ("DELETE", r"^/api/v1/opa/policies/[^/]+/?$", ADMIN_PERMISSION),
    # Decision matrix
    ("GET", r"^/api/v1/decision-matrix/?$", ADMIN_PERMISSION),
    # DB browser
    ("GET", r"^/api/v1/db/.+$", ADMIN_PERMISSION),
    ("POST", r"^/api/v1/db/query/?$", ADMIN_PERMISSION),
]


# Paths that bypass auth entirely — read-only health + docs + the hot path.
PUBLIC_PATHS: tuple[str, ...] = (
    "/health",
    "/health-check",
    "/health-check/",
    "/metrics",
    "/openapi.json",
    "/docs",
    "/redoc",
    # /policies/evaluate is the hot path services (and ds-auth itself) call
    # unauthenticated to resolve permissions. Pinning it down with a
    # service:evaluate permission is a Phase-2 item.
    "/api/v1/policies/evaluate",
    "/api/v1/policies/evaluate/",
)
