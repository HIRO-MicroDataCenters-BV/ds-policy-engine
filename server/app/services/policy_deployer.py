"""
Policy deployment service.

Orchestrates: load rules -> generate Rego -> push to engine.
"""

import logging
from datetime import datetime, timezone

from app.adapters.policy_engine import PolicyEngine
from app.core.exceptions import PolicyDeploymentError
from app.repositories.rule_repository import RuleRepository
from app.services.rego_generator import RegoGenerationStrategy

logger = logging.getLogger("policy_engine.policy_deployer")


class PolicyDeployerService:
    """Generates Rego and deploys to the policy engine."""

    def __init__(
        self,
        engine: PolicyEngine,
        repository: RuleRepository,
        rego_strategy: RegoGenerationStrategy,
    ):
        self._engine = engine
        self._repo = repository
        self._strategy = rego_strategy

    async def deploy(self, deployed_by: str = "system") -> dict:
        """Execute a full deploy cycle: generate Rego and push to engine.

        Loads the current rule manifest from the repository, generates Rego source
        code via the configured strategy, pushes it to the policy engine, and
        updates the manifest timestamp.

        Args:
            deployed_by: Name of the user triggering the deploy.

        Returns:
            dict: Deployment summary containing:
                - deployed_at (str): ISO 8601 UTC timestamp of the deployment.
                - rego (str): The generated Rego source code.
                - rules_count (int): Number of enabled rules that were deployed.
                - version (int): Auto-incremented deploy version.
                - deployed_by (str): User who triggered the deploy.

        Raises:
            PolicyDeploymentError: If the policy engine rejects the push.
        """
        manifest = await self._repo.get_manifest()
        rules = manifest.get("rules", [])

        # Generate Rego using the configured strategy
        rego = self._strategy.generate(rules)

        # Push to engine
        pushed = await self._engine.push_policy("ds_authz", rego)
        if not pushed:
            raise PolicyDeploymentError("Failed to push policy to engine")

        # Update manifest timestamp
        deployed_at = datetime.now(timezone.utc).isoformat()
        manifest["last_deployed"] = deployed_at
        await self._repo.save_manifest(manifest)

        # Append to deploy history table
        enabled_rules = [r for r in rules if r.get("enabled", True)]
        history_entry = {
            "deployed_at": deployed_at,
            "deployed_by": deployed_by,
            "rules_count": len(enabled_rules),
            "roles": sorted({r.get("role") for r in enabled_rules if r.get("role")}),
        }
        version = None
        try:
            result = await self._repo.append_deploy_history(history_entry)
            version = result.get("version")
        except Exception:
            logger.warning("Failed to save deploy history", exc_info=True)

        logger.info("Policy deployed successfully (v%s by %s)", version, deployed_by)
        return {
            "deployed_at": deployed_at,
            "rego": rego,
            "rules_count": len(enabled_rules),
            "version": version,
            "deployed_by": deployed_by,
        }

    async def get_deploy_history(self, limit: int = 20) -> list[dict]:
        """Retrieve deploy history from the deploy_history table."""
        return await self._repo.get_deploy_history(limit=limit)

    async def preview(self, rules: list[dict] | None = None) -> str:
        """Preview the generated Rego source without deploying to the engine.

        Args:
            rules: Optional list of rule dicts to generate Rego from. If None,
                the current manifest rules are loaded from the repository.

        Returns:
            str: The generated Rego source code.
        """
        if rules is None:
            manifest = await self._repo.get_manifest()
            rules = manifest.get("rules", [])
        return self._strategy.generate(rules)

    async def startup_deploy(self) -> bool:
        """Push current policies to the engine during application startup.

        Loads rules from the manifest and pushes the generated Rego to the policy
        engine. Unlike ``deploy``, this method does not update the manifest
        timestamp or save files to disk.

        Returns:
            bool: True if the push succeeded or there were no rules to deploy,
                False if the engine rejected the push.
        """
        manifest = await self._repo.get_manifest()
        rules = manifest.get("rules", [])
        if not rules:
            logger.info("No rules to deploy on startup")
            return True

        rego = self._strategy.generate(rules)
        pushed = await self._engine.push_policy("ds_authz", rego)
        logger.info("Startup deploy: pushed=%s, rules=%d", pushed, len(rules))
        return pushed
