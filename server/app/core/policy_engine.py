"""
Abstract interface (Protocol) for the policy engine.

This is the core abstraction that decouples the application from OPA.
To switch to Cedar, Casbin, or any other engine:
  1. Create a new adapter implementing this Protocol
  2. Update dependencies.py to wire the new adapter
  3. No other code changes needed
"""

from typing import Protocol


class PolicyEngine(Protocol):
    """Port interface for any policy evaluation engine."""

    async def evaluate(self, input_data: dict) -> dict:
        """
        Evaluate policy against input data.

        Args:
            input_data: Policy input (role, institute, etc.)

        Returns:
            Decision dict with permissions list.

        Raises:
            PolicyEngineUnreachableError: Engine is not available.
            PolicyEvaluationError: Evaluation failed.
        """
        ...

    async def push_policy(self, policy_id: str, policy_content: str) -> bool:
        """
        Deploy a policy to the engine.

        Args:
            policy_id: Unique identifier for the policy.
            policy_content: Raw policy content (e.g. Rego source).

        Returns:
            True if successfully pushed.
        """
        ...

    async def list_policies(self) -> list[dict]:
        """List all loaded policies from the engine."""
        ...

    async def delete_policy(self, policy_id: str) -> bool:
        """Remove a policy from the engine."""
        ...

    async def health_check(self) -> bool:
        """Check if the engine is reachable and healthy."""
        ...
