"""
OPA (Open Policy Agent) adapter — concrete implementation of PolicyEngine.

All OPA-specific HTTP communication is isolated here.
Swap this file to switch from OPA to another policy engine.
"""

import logging

import httpx

from app.config import Settings
from app.core.exceptions import PolicyEngineUnreachableError, PolicyEvaluationError

logger = logging.getLogger("policy_engine.opa_adapter")


class OpaAdapter:
    """OPA implementation of the PolicyEngine protocol."""

    def __init__(self, config: Settings):
        self._base_url = config.opa_base_url
        self._timeout = config.opa_timeout
        self._policy_path = config.opa_policy_path
        self._data_url = f"{self._base_url}/v1/data/{self._policy_path}"

    async def evaluate(self, input_data: dict) -> dict:
        """Post input data to OPA and return the policy decision.

        Args:
            input_data: Dictionary of input attributes (e.g. role, user info)
                sent as ``{"input": input_data}`` to the OPA Data API.

        Returns:
            dict: The decision result from OPA. Contains at minimum a
            ``permissions`` key (list of strings). Returns
            ``{"permissions": []}`` when OPA returns an empty result.

        Raises:
            PolicyEngineUnreachableError: If OPA cannot be reached or a
                non-HTTP communication error occurs.
            PolicyEvaluationError: If OPA returns a non-2xx HTTP status.
        """
        try:
            logger.debug("POST %s input=%s", self._data_url, input_data)
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(self._data_url, json={"input": input_data})
                resp.raise_for_status()
                result = resp.json().get("result", {})
                logger.debug("OPA response: %s", result)
                return result if result else {"permissions": []}
        except httpx.ConnectError as exc:
            logger.error("OPA unreachable: %s", exc)
            raise PolicyEngineUnreachableError(
                f"Policy engine unreachable at {self._base_url}"
            ) from exc
        except httpx.HTTPStatusError as exc:
            logger.error(
                "OPA evaluation failed: %s %s",
                exc.response.status_code,
                exc.response.text,
            )
            raise PolicyEvaluationError(
                f"Policy evaluation returned {exc.response.status_code}"
            ) from exc
        except httpx.HTTPError as exc:
            logger.error("OPA HTTP error: %s", exc)
            raise PolicyEngineUnreachableError(
                "Policy engine communication error"
            ) from exc

    async def push_policy(self, policy_id: str, policy_content: str) -> bool:
        """Push a Rego policy to OPA via the Policy API (PUT).

        Args:
            policy_id: Identifier under which the policy is stored in OPA
                (e.g. ``"ds_authz"``).
            policy_content: Raw Rego source code to upload.

        Returns:
            bool: True if OPA accepted the policy (HTTP 200), False otherwise.

        Raises:
            PolicyEngineUnreachableError: If OPA cannot be reached.
        """
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.put(
                    f"{self._base_url}/v1/policies/{policy_id}",
                    content=policy_content.encode("utf-8"),
                    headers={"Content-Type": "text/plain"},
                )
                if resp.status_code == 200:
                    logger.info("Pushed policy '%s' to OPA", policy_id)
                    return True
                logger.error(
                    "Failed to push '%s': %s %s",
                    policy_id,
                    resp.status_code,
                    resp.text,
                )
                return False
        except httpx.HTTPError as exc:
            logger.error("OPA unreachable pushing '%s': %s", policy_id, exc)
            raise PolicyEngineUnreachableError(
                f"Cannot push policy: engine unreachable at {self._base_url}"
            ) from exc

    async def list_policies(self) -> list[dict]:
        """List all policies currently loaded in OPA.

        Returns:
            list[dict]: Policy objects as returned by the OPA ``GET /v1/policies``
            endpoint. Each dict contains fields like ``id``, ``raw``, and ``ast``.

        Raises:
            PolicyEngineUnreachableError: If OPA cannot be reached.
        """
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.get(f"{self._base_url}/v1/policies")
                resp.raise_for_status()
                data = resp.json()
                return data.get("result", [])
        except httpx.HTTPError as exc:
            logger.error("OPA unreachable listing policies: %s", exc)
            raise PolicyEngineUnreachableError() from exc

    async def delete_policy(self, policy_id: str) -> bool:
        """Delete a policy from OPA by its identifier.

        Args:
            policy_id: The OPA policy identifier to delete.

        Returns:
            bool: True if OPA returned HTTP 200 (policy deleted), False
            otherwise (e.g. policy not found).

        Raises:
            PolicyEngineUnreachableError: If OPA cannot be reached.
        """
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.delete(f"{self._base_url}/v1/policies/{policy_id}")
                return resp.status_code == 200
        except httpx.HTTPError as exc:
            logger.error("OPA unreachable deleting '%s': %s", policy_id, exc)
            raise PolicyEngineUnreachableError() from exc

    async def health_check(self) -> bool:
        """Check whether OPA is reachable via its health endpoint.

        Returns:
            bool: True if OPA responds with HTTP 200 on ``/health``,
            False on any HTTP or connection error.
        """
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.get(f"{self._base_url}/health")
                return resp.status_code == 200
        except httpx.HTTPError:
            return False
