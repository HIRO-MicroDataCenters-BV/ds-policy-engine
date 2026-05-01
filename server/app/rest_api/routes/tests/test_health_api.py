"""
Integration tests for Health and OPA Management APIs.
"""


class TestHealthEndpoint:
    """Tests for GET /health endpoint.

    Covers status fields, engine connectivity, and response envelope
    structure.
    """

    def test_health_check(self, test_client):
        """Verify that GET /health returns 200 with service and engine OK."""
        resp = test_client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert body["data"]["service"] == "ok"
        assert body["data"]["policy_engine"] == "ok"
        assert "version" in body["data"]

    def test_health_envelope_structure(self, test_client):
        """Verify that the health response contains all standard envelope keys."""
        resp = test_client.get("/health")
        body = resp.json()
        assert set(body.keys()) == {
            "status",
            "status_code",
            "message",
            "data",
            "error",
            "metadata",
        }


class TestDecisionMatrixEndpoint:
    """Tests for GET /api/v1/decision-matrix endpoint.

    Covers role coverage, permission flags, and response structure.
    """

    def test_decision_matrix(self, test_client):
        """Verify that the decision matrix returns entries for all 3 roles."""
        resp = test_client.get("/api/v1/decision-matrix")
        assert resp.status_code == 200
        body = resp.json()
        matrix = body["data"]["matrix"]
        assert len(matrix) == 3  # 3 roles
        roles_in_matrix = [m["role"] for m in matrix]
        assert "catalog_owner" in roles_in_matrix
        assert "catalog_creator" in roles_in_matrix
        assert "catalog_consumer" in roles_in_matrix

    def test_decision_matrix_owner_has_all(self, test_client):
        """Verify that catalog_owner has all permission flags set to True."""
        resp = test_client.get("/api/v1/decision-matrix")
        matrix = resp.json()["data"]["matrix"]
        owner = next(m for m in matrix if m["role"] == "catalog_owner")
        assert owner["catalog_read"] is True
        assert owner["catalog_create"] is True
        assert owner["catalog_delete"] is True
        assert owner["decentralized_search_execute"] is True
        assert owner["federated_learning_execute"] is True

    def test_decision_matrix_consumer_read_only(self, test_client):
        """Verify that catalog_consumer only has catalog_read set to True."""
        resp = test_client.get("/api/v1/decision-matrix")
        matrix = resp.json()["data"]["matrix"]
        consumer = next(m for m in matrix if m["role"] == "catalog_consumer")
        assert consumer["catalog_read"] is True
        assert consumer["catalog_create"] is False
        assert consumer["decentralized_search_execute"] is False
        assert consumer["federated_learning_execute"] is False

    def test_decision_matrix_returns_permissions_list(self, test_client):
        """The response should include a dynamic list of all known permissions."""
        resp = test_client.get("/api/v1/decision-matrix")
        body = resp.json()
        assert "permissions" in body["data"]
        assert "catalog:read" in body["data"]["permissions"]


class TestOpaManagementEndpoint:
    """Tests for OPA management endpoints.

    Covers policy listing and OPA health status.
    """

    def test_list_opa_policies(self, test_client):
        """Verify that listing OPA policies returns 200 with a policies key."""
        resp = test_client.get("/api/v1/opa/policies")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert "policies" in body["data"]

    def test_opa_health(self, test_client):
        """Verify that the OPA health endpoint reports healthy=True."""
        resp = test_client.get("/api/v1/opa/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["healthy"] is True
