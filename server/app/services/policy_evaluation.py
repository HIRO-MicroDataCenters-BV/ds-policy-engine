"""
Policy evaluation service.

Orchestrates: request -> build input -> call adapter -> format response.
This is the core business logic for the evaluate endpoint.
"""

import logging

from app.adapters.policy_engine import PolicyEngine
from app.models.policy import PolicyEvaluationRequest

logger = logging.getLogger("policy_engine.policy_evaluation")


class PolicyEvaluationService:
    """Evaluates policies by delegating to the policy engine adapter."""

    def __init__(self, engine: PolicyEngine):
        self._engine = engine

    async def evaluate(self, request: PolicyEvaluationRequest) -> dict:
        """
        Evaluate a user's permissions based on their role and institute.

        Args:
            request: The policy evaluation request with name, email, role, institute.

        Returns:
            Dict with "permissions" key containing list of permission strings.
        """
        # Build the input document for the policy engine
        input_data = {
            "name": request.name,
            "email": request.email,
            "role": request.role,
            "institute": request.institute,
        }

        logger.info("Evaluating: role=%s institute=%s", request.role, request.institute)
        logger.debug("Evaluation input: %s", input_data)

        # Delegate to the engine adapter (OPA, Cedar, etc.)
        result = await self._engine.evaluate(input_data)

        permissions = result.get("permissions", [])

        logger.info("Decision: role=%s permissions=%d", request.role, len(permissions))
        logger.debug("Granted: %s", permissions)

        return {"permissions": permissions}
