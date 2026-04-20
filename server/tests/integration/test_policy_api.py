"""
Integration tests for the Policy Evaluation API.

Tests the full HTTP request/response cycle through FastAPI,
including response envelope structure, status codes, and error handling.
"""


class TestEvaluateEndpoint:
    """Tests for POST /api/v1/policies/evaluate including role-based permissions, validation errors, and response envelope structure."""

    def test_evaluate_catalog_owner(self, test_client):
        """Verify that evaluating catalog_owner returns all 6 permissions with correct envelope."""
        resp = test_client.post(
            "/api/v1/policies/evaluate",
            json={
                "name": "John",
                "email": "j@uva.nl",
                "role": "catalog_owner",
                "institute": "uva",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        # Envelope structure
        assert body["status"] == "success"
        assert body["status_code"] == 200
        assert body["error"] is None
        assert "metadata" in body
        assert "timestamp" in body["metadata"]
        assert "request_id" in body["metadata"]
        assert "version" in body["metadata"]
        # Data
        assert "permissions" in body["data"]
        assert len(body["data"]["permissions"]) == 6

    def test_evaluate_catalog_consumer(self, test_client):
        """Verify that evaluating catalog_consumer returns only catalog:read."""
        resp = test_client.post(
            "/api/v1/policies/evaluate",
            json={
                "name": "Jane",
                "email": "j@vu.nl",
                "role": "catalog_consumer",
                "institute": "vu",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["permissions"] == ["catalog:read"]

    def test_evaluate_catalog_creator(self, test_client):
        """Verify that evaluating catalog_creator returns CRUD but not search/FL permissions."""
        resp = test_client.post(
            "/api/v1/policies/evaluate",
            json={
                "name": "Bob",
                "email": "b@amc.nl",
                "role": "catalog_creator",
                "institute": "amc",
            },
        )
        body = resp.json()
        perms = body["data"]["permissions"]
        assert "catalog:read" in perms
        assert "catalog:create" in perms
        assert "catalog:update" in perms
        assert "catalog:delete" in perms
        assert "decentralized-search:execute" not in perms
        assert "federated-learning:execute" not in perms

    def test_evaluate_missing_fields_returns_422(self, test_client):
        """Verify that omitting required fields returns a 422 validation error."""
        resp = test_client.post(
            "/api/v1/policies/evaluate",
            json={
                "name": "John",
                # missing email, role, institute
            },
        )
        assert resp.status_code == 422

    def test_evaluate_empty_role(self, test_client):
        """Verify that an empty role string returns a 422 validation error."""
        resp = test_client.post(
            "/api/v1/policies/evaluate",
            json={
                "name": "X",
                "email": "x@x.nl",
                "role": "",
                "institute": "uva",
            },
        )
        # FastAPI validation should catch min_length=1
        assert resp.status_code == 422

    def test_evaluate_response_envelope_structure(self, test_client):
        """Verify that the evaluate response has all required envelope and metadata keys."""
        resp = test_client.post(
            "/api/v1/policies/evaluate",
            json={
                "name": "T",
                "email": "t@t.nl",
                "role": "catalog_owner",
                "institute": "t",
            },
        )
        body = resp.json()
        # All required envelope fields present
        assert set(body.keys()) == {"status", "status_code", "message", "data", "error", "metadata"}
        assert set(body["metadata"].keys()) == {"timestamp", "request_id", "version"}


class TestDeployEndpoint:
    """Tests for POST /api/v1/policies/deploy including Rego generation, deployment timestamp, and rules count."""

    def test_deploy_success(self, test_client):
        """Verify that deploying policies returns 200 with Rego and deployed_at."""
        resp = test_client.post("/api/v1/policies/deploy")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert "deployed_at" in body["data"]
        assert "rego" in body["data"]
        assert "package ds.authz" in body["data"]["rego"]

    def test_deploy_returns_rules_count(self, test_client):
        """Verify that deploy response includes the correct rules_count."""
        resp = test_client.post("/api/v1/policies/deploy")
        body = resp.json()
        assert body["data"]["rules_count"] == 3


class TestPreviewEndpoint:
    """Tests for POST /api/v1/policies/preview which generates Rego without deploying to the engine."""

    def test_preview_returns_rego(self, test_client):
        """Verify that preview returns generated Rego without deploying."""
        resp = test_client.post("/api/v1/policies/preview")
        assert resp.status_code == 200
        body = resp.json()
        assert "rego" in body["data"]
        assert "package ds.authz" in body["data"]["rego"]
