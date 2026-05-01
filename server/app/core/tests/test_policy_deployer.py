"""
Unit tests for the policy deployer service.

Tests the deploy cycle: generate Rego -> push to engine.
Uses mock engine and in-memory repository.
"""

import pytest

from app.core.rego_generator import PermissionBasedRegoStrategy
from app.core.usecases import PolicyDeployerUsecase


@pytest.fixture
def service(mock_engine, mock_repo_with_seed):
    return PolicyDeployerUsecase(
        engine=mock_engine,
        repository=mock_repo_with_seed,
        rego_strategy=PermissionBasedRegoStrategy(),
    )


class TestDeploy:
    """Tests for the full deploy cycle."""

    @pytest.mark.asyncio
    async def test_deploy_returns_rego(self, service):
        """Verify that deploy returns a result containing valid Rego source."""
        result = await service.deploy()
        assert "rego" in result
        assert "package ds.authz" in result["rego"]

    @pytest.mark.asyncio
    async def test_deploy_returns_deployed_at(self, service):
        """Verify that deploy returns a non-null deployed_at timestamp."""
        result = await service.deploy()
        assert "deployed_at" in result
        assert result["deployed_at"] is not None

    @pytest.mark.asyncio
    async def test_deploy_returns_rules_count(self, service):
        """Verify that deploy reports the correct number of deployed rules."""
        result = await service.deploy()
        assert result["rules_count"] == 3

    @pytest.mark.asyncio
    async def test_deploy_pushes_to_engine(self, service, mock_engine):
        """Verify that deploy pushes the generated policy to the mock engine."""
        await service.deploy()
        policies = await mock_engine.list_policies()
        assert len(policies) == 1
        assert policies[0]["id"] == "ds_authz"

    @pytest.mark.asyncio
    async def test_deploy_updates_manifest_timestamp(
        self, service, mock_repo_with_seed
    ):
        """Verify that deploy sets the last_deployed timestamp in the manifest."""
        await service.deploy()
        manifest = await mock_repo_with_seed.get_manifest()
        assert manifest["last_deployed"] is not None


class TestPreview:
    """Tests for Rego preview (no deployment)."""

    @pytest.mark.asyncio
    async def test_preview_returns_rego(self, service):
        """Verify that preview generates Rego source without deploying."""
        rego = await service.preview()
        assert "package ds.authz" in rego

    @pytest.mark.asyncio
    async def test_preview_does_not_push(self, service, mock_engine):
        """Verify that preview does not push any policy to the engine."""
        await service.preview()
        policies = await mock_engine.list_policies()
        assert len(policies) == 0

    @pytest.mark.asyncio
    async def test_preview_custom_rules(self, service):
        """Verify that preview can generate Rego from a custom rules list."""
        custom = [
            {
                "id": "x",
                "name": "X",
                "role": "catalog_owner",
                "permissions": ["catalog:read"],
                "enabled": True,
            }
        ]
        rego = await service.preview(rules=custom)
        assert 'input.role == "catalog_owner"' in rego


class TestStartupDeploy:
    """Tests for startup deployment."""

    @pytest.mark.asyncio
    async def test_startup_deploy_pushes_policies(self, service, mock_engine):
        """Verify that startup_deploy pushes policies to the engine on boot."""
        result = await service.startup_deploy()
        assert result is True
        policies = await mock_engine.list_policies()
        assert len(policies) == 1

    @pytest.mark.asyncio
    async def test_startup_deploy_empty_rules(self, mock_engine, mock_repo):
        """Verify startup_deploy with no rules succeeds without pushing."""
        svc = PolicyDeployerUsecase(
            engine=mock_engine,
            repository=mock_repo,
            rego_strategy=PermissionBasedRegoStrategy(),
        )
        result = await svc.startup_deploy()
        assert result is True
        policies = await mock_engine.list_policies()
        assert len(policies) == 0
