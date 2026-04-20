"""
Integration tests for the API with SQLite database backend.

Unlike the other integration tests (which use InMemoryRuleRepository),
these tests wire a real SQLite database through the full HTTP cycle
to verify the complete stack: HTTP -> Routes -> Services -> SQLite.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Base
from app.repositories.sqlite_rule_repository import SqliteRuleRepository


@pytest.fixture
def sqlite_test_client(mock_engine, temp_policies_dir):
    """
    FastAPI test client backed by a real in-memory SQLite database.

    Uses SqliteRuleRepository instead of InMemoryRuleRepository,
    testing the full persistence stack.
    """
    import asyncio

    from app.core import dependencies
    from app.main import app
    from app.services.rego_generator import PermissionBasedRegoStrategy

    # Create in-memory SQLite
    loop = asyncio.new_event_loop()
    engine = loop.run_until_complete(_create_test_db())

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    sqlite_repo = SqliteRuleRepository(factory)

    # Pre-seed 3 rules
    loop.run_until_complete(_seed_test_rules(sqlite_repo))

    # Override dependency injection
    dependencies.get_policy_engine = lambda: mock_engine
    dependencies.get_rule_repository = lambda: sqlite_repo
    dependencies.get_rego_strategy = lambda: PermissionBasedRegoStrategy()

    dependencies.get_policy_evaluation_service = lambda: __import__(
        "app.services.policy_evaluation", fromlist=["PolicyEvaluationService"]
    ).PolicyEvaluationService(engine=mock_engine)

    dependencies.get_rule_management_service = lambda: __import__(
        "app.services.rule_management", fromlist=["RuleManagementService"]
    ).RuleManagementService(repository=sqlite_repo)

    dependencies.get_policy_deployer_service = lambda: __import__(
        "app.services.policy_deployer", fromlist=["PolicyDeployerService"]
    ).PolicyDeployerService(
        engine=mock_engine,
        repository=sqlite_repo,
        rego_strategy=PermissionBasedRegoStrategy(),
    )

    dependencies.get_decision_matrix_service = lambda: __import__(
        "app.services.decision_matrix", fromlist=["DecisionMatrixService"]
    ).DecisionMatrixService(engine=mock_engine, repository=sqlite_repo)

    client = TestClient(app)
    yield client

    loop.run_until_complete(engine.dispose())
    loop.close()


async def _create_test_db():
    """Create an in-memory SQLite async engine and initialize all ORM tables from Base metadata."""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine


async def _seed_test_rules(repo: SqliteRuleRepository):
    """Insert three test rules (owner, creator, consumer) directly into the SQLite repository for integration testing."""
    rules = [
        {
            "name": "Catalog Owner Full Access",
            "role": "catalog_owner",
            "permissions": [
                "catalog:read", "catalog:create", "catalog:update",
                "catalog:delete", "decentralized-search:execute",
                "federated-learning:execute",
            ],
        },
        {
            "name": "Catalog Creator Local CRUD",
            "role": "catalog_creator",
            "permissions": ["catalog:read", "catalog:create", "catalog:update", "catalog:delete"],
        },
        {
            "name": "Catalog Consumer Read Only",
            "role": "catalog_consumer",
            "permissions": ["catalog:read"],
        },
    ]
    for rule in rules:
        await repo.create_rule(rule)


class TestRulesCRUDWithSQLite:
    """Tests for full CRUD operations through HTTP with a real SQLite backend, verifying persistence and conflict handling."""

    def test_list_rules(self, sqlite_test_client):
        """Verify that listing rules via SQLite backend returns all 3 seeded rules."""
        resp = sqlite_test_client.get("/api/v1/rules")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["data"]["rules"]) == 3

    def test_create_rule(self, sqlite_test_client):
        """Verify that creating a rule persists it in SQLite and is fetchable."""
        resp = sqlite_test_client.post(
            "/api/v1/rules",
            json={
                "name": "New SQLite Rule",
                "role": "data_steward",
                "permissions": ["catalog:read"],
            },
        )
        assert resp.status_code == 201
        rule = resp.json()["data"]["rule"]
        assert rule["name"] == "New SQLite Rule"
        assert rule["id"].startswith("rule-")

        # Verify persisted
        resp2 = sqlite_test_client.get(f"/api/v1/rules/{rule['id']}")
        assert resp2.status_code == 200
        assert resp2.json()["data"]["rule"]["name"] == "New SQLite Rule"

    def test_update_rule(self, sqlite_test_client):
        """Verify that updating a rule via SQLite backend persists the change."""
        # Get an existing rule
        rules = sqlite_test_client.get("/api/v1/rules").json()["data"]["rules"]
        rule_id = rules[0]["id"]

        resp = sqlite_test_client.put(
            f"/api/v1/rules/{rule_id}",
            json={"name": "Updated via SQLite"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["rule"]["name"] == "Updated via SQLite"

    def test_delete_rule(self, sqlite_test_client):
        """Verify that deleting a rule via SQLite backend removes it permanently."""
        # Get an existing rule
        rules = sqlite_test_client.get("/api/v1/rules").json()["data"]["rules"]
        rule_id = rules[0]["id"]

        resp = sqlite_test_client.delete(f"/api/v1/rules/{rule_id}")
        assert resp.status_code == 200

        # Verify deleted
        resp2 = sqlite_test_client.get(f"/api/v1/rules/{rule_id}")
        assert resp2.status_code == 404

    def test_toggle_rule(self, sqlite_test_client):
        """Verify that toggling a rule via SQLite backend flips its enabled state."""
        rules = sqlite_test_client.get("/api/v1/rules").json()["data"]["rules"]
        rule_id = rules[0]["id"]

        resp = sqlite_test_client.patch(f"/api/v1/rules/{rule_id}/toggle")
        assert resp.status_code == 200
        assert resp.json()["data"]["rule"]["enabled"] is False

    def test_create_duplicate_returns_409(self, sqlite_test_client):
        """Verify that creating a rule with a duplicate name returns 409 via SQLite."""
        resp = sqlite_test_client.post(
            "/api/v1/rules",
            json={
                "name": "Catalog Owner Full Access",
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
            },
        )
        assert resp.status_code == 409


class TestDeployWithSQLite:
    """Tests for deploy and preview endpoints reading rules from a real SQLite database."""

    def test_deploy_reads_from_sqlite(self, sqlite_test_client):
        """Verify that deploy generates Rego from rules stored in SQLite."""
        resp = sqlite_test_client.post("/api/v1/policies/deploy")
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["rules_count"] == 3
        assert "package ds.authz" in body["data"]["rego"]

    def test_preview_reads_from_sqlite(self, sqlite_test_client):
        """Verify that preview generates Rego from rules stored in SQLite."""
        resp = sqlite_test_client.post("/api/v1/policies/preview")
        assert resp.status_code == 200
        rego = resp.json()["data"]["rego"]
        assert "catalog_owner" in rego
        assert "catalog_consumer" in rego


class TestPersistenceAcrossRequests:
    """Tests that data created, updated, or deleted via one HTTP request is correctly reflected in subsequent requests against the SQLite backend."""

    def test_create_then_list_includes_new_rule(self, sqlite_test_client):
        """Verify that a newly created rule appears in subsequent list requests."""
        # Create
        sqlite_test_client.post(
            "/api/v1/rules",
            json={
                "name": "Persistence Test",
                "role": "node_admin",
                "permissions": ["audit:read"],
            },
        )

        # List should include the new rule
        rules = sqlite_test_client.get("/api/v1/rules").json()["data"]["rules"]
        names = [r["name"] for r in rules]
        assert "Persistence Test" in names
        assert len(rules) == 4

    def test_update_then_get_reflects_change(self, sqlite_test_client):
        """Verify that an updated rule reflects the change on subsequent GET."""
        rules = sqlite_test_client.get("/api/v1/rules").json()["data"]["rules"]
        rule_id = rules[0]["id"]

        sqlite_test_client.put(
            f"/api/v1/rules/{rule_id}",
            json={"permissions": ["catalog:read"]},
        )

        fetched = sqlite_test_client.get(f"/api/v1/rules/{rule_id}").json()
        assert fetched["data"]["rule"]["permissions"] == ["catalog:read"]

    def test_delete_then_deploy_excludes_rule(self, sqlite_test_client):
        """Verify that a deleted rule is excluded from subsequent deploy output."""
        rules = sqlite_test_client.get("/api/v1/rules").json()["data"]["rules"]
        rule_id = rules[0]["id"]

        sqlite_test_client.delete(f"/api/v1/rules/{rule_id}")

        deploy = sqlite_test_client.post("/api/v1/policies/deploy").json()
        assert deploy["data"]["rules_count"] == 2
