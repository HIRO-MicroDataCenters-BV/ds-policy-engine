"""
Shared test fixtures for unit and integration tests.

Provides:
  - Mock policy engine adapter (no OPA dependency)
  - In-memory rule repository (no file I/O)
  - FastAPI test client
"""

from typing import Any, cast

import json
import tempfile
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.constants import DEFAULT_ROLE_PERMISSIONS
from app.core.repository.db_models import Base

# ---------------------------------------------------------------------------
# Mock Policy Engine (replaces OPA in tests)
# ---------------------------------------------------------------------------


class MockPolicyEngine:
    """In-memory policy engine that mimics OPA behavior."""

    def __init__(self):
        self._policies: dict[str, str] = {}
        self._healthy = True
        # Simulate the decision logic from Rego
        self._role_permissions = dict(DEFAULT_ROLE_PERMISSIONS)

    async def evaluate(self, input_data: dict) -> dict:
        """Return permissions for the given role based on the default role map."""
        role = input_data.get("role", "")
        permissions = self._role_permissions.get(role, [])
        return {"permissions": list(permissions)}

    async def push_policy(self, policy_id: str, policy_content: str) -> bool:
        """Store a policy in memory and return True."""
        self._policies[policy_id] = policy_content
        return True

    async def list_policies(self) -> list[dict]:
        """Return all stored policies as a list of dicts."""
        return [{"id": pid, "raw": content} for pid, content in self._policies.items()]

    async def delete_policy(self, policy_id: str) -> bool:
        """Remove a policy by ID; return True if it existed, False otherwise."""
        if policy_id in self._policies:
            del self._policies[policy_id]
            return True
        return False

    async def health_check(self) -> bool:
        """Return the current health status."""
        return self._healthy

    def set_unhealthy(self):
        """Mark the mock engine as unhealthy."""
        self._healthy = False

    def set_healthy(self):
        """Mark the mock engine as healthy."""
        self._healthy = True


# ---------------------------------------------------------------------------
# In-memory Rule Repository
# ---------------------------------------------------------------------------


class InMemoryRuleRepository:
    """In-memory rule storage for testing (no file I/O)."""

    def __init__(self, initial_rules: list[dict] | None = None):
        # ``_manifest`` mirrors the on-disk JSON shape (mixed value types:
        # version/int, last_deployed/str|None, rules/list[dict]) so the
        # value type is intentionally ``Any`` and rule access goes through
        # ``_rules()`` for narrowing.
        self._manifest: dict[str, Any] = {
            "version": 1,
            "last_deployed": None,
            "rules": list(initial_rules) if initial_rules else [],
        }

    def _rules(self) -> list[dict]:
        """Return the typed rules list from the manifest, creating it if absent."""
        return cast(list[dict], self._manifest.setdefault("rules", []))

    async def get_manifest(self) -> dict:
        """Return a shallow copy of the current manifest."""
        return dict(self._manifest)

    async def save_manifest(self, manifest: dict) -> None:
        """Replace the stored manifest with the provided one."""
        self._manifest = dict(manifest)

    async def list_rules(self) -> list[dict]:
        """Return a copy of all rules in the manifest."""
        return list(self._rules())

    async def get_rule(self, rule_id: str) -> dict | None:
        """Return a single rule by ID, or None if not found."""
        return next((r for r in self._rules() if r["id"] == rule_id), None)

    async def create_rule(self, rule: dict) -> dict:
        """Add a new rule with auto-generated ID and timestamps."""
        now = datetime.now(timezone.utc).isoformat()
        rule["id"] = f"rule-{uuid4().hex[:6]}"
        rule["created_at"] = now
        rule["updated_at"] = now
        rule.setdefault("enabled", True)
        self._rules().append(rule)
        return rule

    async def update_rule(self, rule_id: str, updates: dict) -> dict | None:
        """Apply updates to an existing rule; return None if not found."""
        rules = self._rules()
        for i, r in enumerate(rules):
            if r["id"] == rule_id:
                updated = {**r, **{k: v for k, v in updates.items() if v is not None}}
                updated["id"] = rule_id
                updated["updated_at"] = datetime.now(timezone.utc).isoformat()
                rules[i] = updated
                return updated
        return None

    async def delete_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID; return True if it was removed."""
        rules = self._rules()
        before = len(rules)
        self._manifest["rules"] = [r for r in rules if r["id"] != rule_id]
        return len(self._manifest["rules"]) < before


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_engine():
    """Provide a fresh MockPolicyEngine instance with default role permissions."""
    return MockPolicyEngine()


@pytest.fixture
def mock_repo():
    """Provide an empty InMemoryRuleRepository with no pre-loaded rules."""
    return InMemoryRuleRepository()


@pytest.fixture
def mock_repo_with_seed():
    """Provide an InMemoryRuleRepository pre-loaded with three seed rules.

    Rules are for: catalog_owner, catalog_creator, and catalog_consumer.
    """
    return InMemoryRuleRepository(
        [
            {
                "id": "rule-owner-full",
                "name": "Catalog Owner Full Access",
                "description": "Full permissions",
                "role": "catalog_owner",
                "permissions": [
                    "catalog:read",
                    "catalog:create",
                    "catalog:update",
                    "catalog:delete",
                    "decentralized-search:execute",
                    "federated-learning:execute",
                ],
                "enabled": True,
                "created_at": "2026-04-02T00:00:00Z",
                "updated_at": "2026-04-02T00:00:00Z",
            },
            {
                "id": "rule-creator-local",
                "name": "Catalog Creator Local CRUD",
                "description": "Local CRUD only",
                "role": "catalog_creator",
                "permissions": [
                    "catalog:read",
                    "catalog:create",
                    "catalog:update",
                    "catalog:delete",
                ],
                "enabled": True,
                "created_at": "2026-04-02T00:00:00Z",
                "updated_at": "2026-04-02T00:00:00Z",
            },
            {
                "id": "rule-consumer-read",
                "name": "Catalog Consumer Read Only",
                "description": "Read only",
                "role": "catalog_consumer",
                "permissions": ["catalog:read"],
                "enabled": True,
                "created_at": "2026-04-02T00:00:00Z",
                "updated_at": "2026-04-02T00:00:00Z",
            },
        ]
    )


@pytest.fixture
def temp_policies_dir():
    """Provide a temporary directory that is automatically cleaned up.

    Used for writing Rego files and seed JSON during tests.
    """
    with tempfile.TemporaryDirectory() as d:
        yield d


# ---------------------------------------------------------------------------
# SQLite Database Fixtures (real DB for repository/seed tests)
# ---------------------------------------------------------------------------


@pytest.fixture
async def db_session_factory():
    """Create an in-memory SQLite database with tables for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield factory

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def seed_rules_file(temp_policies_dir):
    """Write a seed_rules.json file with three rules and return its path.

    The file contains owner, creator, and consumer rules and is written
    into ``temp_policies_dir``.
    """
    seed_data = {
        "version": 1,
        "last_deployed": "2026-04-02T00:00:00Z",
        "rules": [
            {
                "id": "rule-owner-full",
                "name": "Catalog Owner Full Access",
                "description": "Full permissions",
                "role": "catalog_owner",
                "permissions": [
                    "catalog:read",
                    "catalog:create",
                    "catalog:update",
                    "catalog:delete",
                    "decentralized-search:execute",
                    "federated-learning:execute",
                ],
                "enabled": True,
                "created_at": "2026-04-02T00:00:00Z",
                "updated_at": "2026-04-02T00:00:00Z",
            },
            {
                "id": "rule-creator-local",
                "name": "Catalog Creator Local CRUD",
                "description": "Local CRUD only",
                "role": "catalog_creator",
                "permissions": [
                    "catalog:read",
                    "catalog:create",
                    "catalog:update",
                    "catalog:delete",
                ],
                "enabled": True,
                "created_at": "2026-04-02T00:00:00Z",
                "updated_at": "2026-04-02T00:00:00Z",
            },
            {
                "id": "rule-consumer-read",
                "name": "Catalog Consumer Read Only",
                "description": "Read only",
                "role": "catalog_consumer",
                "permissions": ["catalog:read"],
                "enabled": True,
                "created_at": "2026-04-02T00:00:00Z",
                "updated_at": "2026-04-02T00:00:00Z",
            },
        ],
    }
    import pathlib

    path = pathlib.Path(temp_policies_dir) / "seed_rules.json"
    path.write_text(json.dumps(seed_data, indent=2), encoding="utf-8")
    return str(path)


@pytest.fixture
def test_client(mock_engine, mock_repo_with_seed, temp_policies_dir):
    """Provide a FastAPI TestClient with all service dependencies overridden.

    Overrides use MockPolicyEngine, a seed-loaded InMemoryRuleRepository,
    and a temporary policies directory.
    """
    from app.core.rego_generator import PermissionBasedRegoStrategy
    from app.main import app
    from app.rest_api import depends as dependencies

    # Override dependency injection
    dependencies.get_policy_engine = lambda: mock_engine
    dependencies.get_rule_repository = lambda: mock_repo_with_seed
    dependencies.get_rego_strategy = lambda: PermissionBasedRegoStrategy()

    # Override services that depend on the above
    dependencies.get_policy_evaluation_usecase = lambda: __import__(
        "app.core.usecases", fromlist=["PolicyEvaluationUsecase"]
    ).PolicyEvaluationUsecase(engine=mock_engine)

    dependencies.get_rule_management_usecase = lambda: __import__(
        "app.core.usecases", fromlist=["RuleManagementUsecase"]
    ).RuleManagementUsecase(repository=mock_repo_with_seed)

    dependencies.get_policy_deployer_usecase = lambda: __import__(
        "app.core.usecases", fromlist=["PolicyDeployerUsecase"]
    ).PolicyDeployerUsecase(
        engine=mock_engine,
        repository=mock_repo_with_seed,
        rego_strategy=PermissionBasedRegoStrategy(),
    )

    dependencies.get_decision_matrix_usecase = lambda: __import__(
        "app.core.usecases", fromlist=["DecisionMatrixUsecase"]
    ).DecisionMatrixUsecase(engine=mock_engine, repository=mock_repo_with_seed)

    return TestClient(app)
