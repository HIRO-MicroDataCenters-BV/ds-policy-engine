"""
Unit tests for the policy evaluation service.

Tests that the service correctly builds OPA input and maps responses.
Uses a mock policy engine (no OPA dependency).
"""

import pytest

from app.models.policy import PolicyEvaluationRequest
from app.services.policy_evaluation import PolicyEvaluationService


@pytest.fixture
def service(mock_engine):
    return PolicyEvaluationService(engine=mock_engine)


class TestPolicyEvaluation:
    """Tests for policy evaluation using mock engine."""

    @pytest.mark.asyncio
    async def test_catalog_owner_gets_all_permissions(self, service):
        """Verify that catalog_owner receives all 6 permissions."""
        request = PolicyEvaluationRequest(
            name="John", email="j@uva.nl", role="catalog_owner", institute="uva"
        )
        result = await service.evaluate(request)
        assert "permissions" in result
        assert len(result["permissions"]) == 6
        assert "catalog:read" in result["permissions"]
        assert "decentralized-search:execute" in result["permissions"]
        assert "federated-learning:execute" in result["permissions"]

    @pytest.mark.asyncio
    async def test_catalog_creator_gets_crud_only(self, service):
        """Verify that catalog_creator gets CRUD permissions but not search or FL."""
        request = PolicyEvaluationRequest(
            name="Jane", email="j@amc.nl", role="catalog_creator", institute="amc"
        )
        result = await service.evaluate(request)
        assert len(result["permissions"]) == 4
        assert "catalog:read" in result["permissions"]
        assert "catalog:create" in result["permissions"]
        assert "decentralized-search:execute" not in result["permissions"]

    @pytest.mark.asyncio
    async def test_catalog_consumer_gets_read_only(self, service):
        """Verify that catalog_consumer receives only catalog:read."""
        request = PolicyEvaluationRequest(
            name="Bob", email="b@vu.nl", role="catalog_consumer", institute="vu"
        )
        result = await service.evaluate(request)
        assert result["permissions"] == ["catalog:read"]

    @pytest.mark.asyncio
    async def test_unknown_role_gets_empty(self, service):
        """Verify that an unrecognized role gets an empty permissions list."""
        request = PolicyEvaluationRequest(
            name="X", email="x@uva.nl", role="unknown", institute="uva"
        )
        result = await service.evaluate(request)
        assert result["permissions"] == []

    @pytest.mark.asyncio
    async def test_result_structure(self, service):
        """Verify that the evaluation result is a dict with a permissions list."""
        request = PolicyEvaluationRequest(
            name="Test", email="t@uva.nl", role="catalog_owner", institute="uva"
        )
        result = await service.evaluate(request)
        assert isinstance(result, dict)
        assert "permissions" in result
        assert isinstance(result["permissions"], list)
