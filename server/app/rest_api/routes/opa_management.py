"""
OPA management proxy routes.

Provides REST endpoints for listing, deleting, and health-checking policies
that are loaded in the OPA policy engine instance.

Tag: OPA Management
"""

from fastapi import APIRouter, Depends

from app.core.opa_adapter import OpaAdapter
from app.rest_api.depends import get_policy_engine
from app.rest_api.response import success_response

router = APIRouter(prefix="/api/v1/opa", tags=["OPA Management"])


@router.get(
    "/policies",
    summary="List OPA policies",
    description="List all policies currently loaded in OPA",
)
async def list_opa_policies(
    engine: OpaAdapter = Depends(get_policy_engine),
):
    """List all policies currently loaded in the OPA engine.

    Returns:
        JSONResponse: A success envelope containing ``data.policies``, a list of
        policy objects as returned by the OPA Policy API.
    """
    policies = await engine.list_policies()
    return success_response(
        data={"policies": policies}, message="OPA policies retrieved"
    )


@router.delete(
    "/policies/{policy_id}",
    summary="Delete OPA policy",
    description="Remove a policy from OPA",
)
async def delete_opa_policy(
    policy_id: str,
    engine: OpaAdapter = Depends(get_policy_engine),
):
    """Delete a specific policy from the OPA engine by its identifier.

    Args:
        policy_id: The OPA policy identifier to remove.
        engine: Injected OPA adapter instance.

    Returns:
        JSONResponse: A success envelope with a message indicating whether the
        policy was deleted or not found.
    """
    deleted = await engine.delete_policy(policy_id)
    msg = (
        f"Policy '{policy_id}' deleted"
        if deleted
        else f"Policy '{policy_id}' not found"
    )
    return success_response(message=msg)


@router.get("/health", summary="OPA health", description="Check if OPA is reachable")
async def opa_health(
    engine: OpaAdapter = Depends(get_policy_engine),
):
    """Check whether the OPA engine is reachable and healthy.

    Returns:
        JSONResponse: A success envelope containing ``data.engine`` ("opa"),
        ``data.healthy`` (bool), and a human-readable status message.
    """
    healthy = await engine.health_check()
    return success_response(
        data={"engine": "opa", "healthy": healthy},
        message="OPA is healthy" if healthy else "OPA is unreachable",
    )
