"""
Integration tests for the Rules CRUD API.

Tests pagination, filtering, CRUD operations, and error handling
through the full HTTP request/response cycle.
"""


class TestListRulesEndpoint:
    """Tests for GET /api/v1/rules.

    Covers pagination, role filtering, text search, and response
    envelope structure.
    """

    def test_list_rules_default(self, test_client):
        """Verify listing without params returns all 3 rules with pagination."""
        resp = test_client.get("/api/v1/rules")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert len(body["data"]["rules"]) == 3
        assert "pagination" in body["data"]

    def test_list_rules_pagination(self, test_client):
        """Verify that pagination limits results and sets correct metadata."""
        resp = test_client.get("/api/v1/rules?page=1&page_size=2")
        body = resp.json()
        assert len(body["data"]["rules"]) == 2
        pg = body["data"]["pagination"]
        assert pg["total_items"] == 3
        assert pg["total_pages"] == 2
        assert pg["has_next"] is True

    def test_list_rules_page_2(self, test_client):
        """Verify that requesting page 2 returns the remaining rule."""
        resp = test_client.get("/api/v1/rules?page=2&page_size=2")
        body = resp.json()
        assert len(body["data"]["rules"]) == 1
        assert body["data"]["pagination"]["has_previous"] is True

    def test_list_rules_filter_role(self, test_client):
        """Verify that filtering by role returns only matching rules."""
        resp = test_client.get("/api/v1/rules?role=catalog_owner")
        body = resp.json()
        assert len(body["data"]["rules"]) == 1
        assert body["data"]["rules"][0]["role"] == "catalog_owner"

    def test_list_rules_search(self, test_client):
        """Verify that search query filters rules by name substring."""
        resp = test_client.get("/api/v1/rules?search=consumer")
        body = resp.json()
        assert len(body["data"]["rules"]) == 1
        assert "Consumer" in body["data"]["rules"][0]["name"]

    def test_list_rules_empty_search(self, test_client):
        """Verify that a search with no matches returns an empty rules list."""
        resp = test_client.get("/api/v1/rules?search=nonexistent")
        body = resp.json()
        assert len(body["data"]["rules"]) == 0
        assert body["data"]["pagination"]["total_items"] == 0

    def test_list_rules_envelope_structure(self, test_client):
        """Verify that the list response has correct envelope and pagination keys."""
        resp = test_client.get("/api/v1/rules")
        body = resp.json()
        assert set(body.keys()) == {
            "status",
            "status_code",
            "message",
            "data",
            "error",
            "metadata",
        }
        pg = body["data"]["pagination"]
        assert set(pg.keys()) == {
            "page",
            "page_size",
            "total_items",
            "total_pages",
            "has_next",
            "has_previous",
        }


class TestCreateRuleEndpoint:
    """Tests for POST /api/v1/rules.

    Covers successful creation, validation errors (400), conflicts
    (409), and missing fields (422).
    """

    def test_create_rule_success(self, test_client):
        """Verify creating a valid rule returns 201 with ID and timestamps."""
        resp = test_client.post(
            "/api/v1/rules",
            json={
                "name": "New Test Rule",
                "description": "Test description",
                "role": "catalog_consumer",
                "permissions": ["catalog:read"],
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "success"
        assert body["status_code"] == 201
        rule = body["data"]["rule"]
        assert rule["name"] == "New Test Rule"
        assert rule["id"].startswith("rule-")
        assert "created_at" in rule

    def test_create_rule_invalid_role_format_returns_400(self, test_client):
        """Role that doesn't match format (starts with digit) should be rejected."""
        resp = test_client.post(
            "/api/v1/rules",
            json={
                "name": "Bad Rule",
                "role": "123bad",
                "permissions": ["catalog:read"],
            },
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body["status"] == "error"
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_create_rule_custom_role_succeeds(self, test_client):
        """Valid custom role (not in seed enums) should be accepted."""
        resp = test_client.post(
            "/api/v1/rules",
            json={
                "name": "Data Steward Rule",
                "role": "data_steward",
                "permissions": ["catalog:read"],
            },
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["rule"]["role"] == "data_steward"

    def test_create_rule_invalid_permission_format_returns_400(self, test_client):
        """Permission without resource:action format should be rejected."""
        resp = test_client.post(
            "/api/v1/rules",
            json={
                "name": "Bad Perm",
                "role": "catalog_owner",
                "permissions": ["NOCOLON"],
            },
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_create_duplicate_returns_409(self, test_client):
        """Verify that creating a rule with a duplicate name returns 409."""
        resp = test_client.post(
            "/api/v1/rules",
            json={
                "name": "Catalog Owner Full Access",  # already exists
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
            },
        )
        assert resp.status_code == 409
        body = resp.json()
        assert body["error"]["code"] == "RULE_CONFLICT"

    def test_create_rule_missing_name_returns_422(self, test_client):
        """Verify that omitting the required name field returns 422."""
        resp = test_client.post(
            "/api/v1/rules",
            json={
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
            },
        )
        assert resp.status_code == 422


class TestGetRuleEndpoint:
    """Tests for GET /api/v1/rules/{rule_id}.

    Covers successful fetch and 404 for missing rules.
    """

    def test_get_existing_rule(self, test_client):
        """Verify fetching an existing rule by ID returns 200 with data."""
        resp = test_client.get("/api/v1/rules/rule-owner-full")
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["rule"]["id"] == "rule-owner-full"

    def test_get_nonexistent_returns_404(self, test_client):
        """Verify that fetching a non-existent rule returns 404 with error details."""
        resp = test_client.get("/api/v1/rules/rule-nope")
        assert resp.status_code == 404
        body = resp.json()
        assert body["status"] == "error"
        assert body["error"]["code"] == "RULE_NOT_FOUND"
        assert body["data"] is None


class TestUpdateRuleEndpoint:
    """Tests for PUT /api/v1/rules/{rule_id}.

    Covers successful updates and 404 for missing rules.
    """

    def test_update_rule_name(self, test_client):
        """Verify that updating a rule's name via PUT returns the renamed rule."""
        resp = test_client.put(
            "/api/v1/rules/rule-owner-full", json={"name": "Renamed"}
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["rule"]["name"] == "Renamed"

    def test_update_nonexistent_returns_404(self, test_client):
        """Verify that updating a non-existent rule returns 404."""
        resp = test_client.put("/api/v1/rules/rule-nope", json={"name": "X"})
        assert resp.status_code == 404


class TestDeleteRuleEndpoint:
    """Tests for DELETE /api/v1/rules/{rule_id}.

    Covers successful deletion with verification and 404 for missing
    rules.
    """

    def test_delete_rule(self, test_client):
        """Verify deleting a rule returns 200 and the rule is unfetchable."""
        resp = test_client.delete("/api/v1/rules/rule-consumer-read")
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"
        # Verify deleted
        resp2 = test_client.get("/api/v1/rules/rule-consumer-read")
        assert resp2.status_code == 404

    def test_delete_nonexistent_returns_404(self, test_client):
        """Verify that deleting a non-existent rule returns 404."""
        resp = test_client.delete("/api/v1/rules/rule-nope")
        assert resp.status_code == 404


class TestToggleRuleEndpoint:
    """Tests for PATCH /api/v1/rules/{rule_id}/toggle.

    Covers toggling enabled state and 404 for missing rules.
    """

    def test_toggle_disables_rule(self, test_client):
        """Verify that toggling an enabled rule sets enabled to False."""
        resp = test_client.patch("/api/v1/rules/rule-owner-full/toggle")
        assert resp.status_code == 200
        assert resp.json()["data"]["rule"]["enabled"] is False

    def test_toggle_nonexistent_returns_404(self, test_client):
        """Verify that toggling a non-existent rule returns 404."""
        resp = test_client.patch("/api/v1/rules/rule-nope/toggle")
        assert resp.status_code == 404
