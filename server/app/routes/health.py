"""
Health check route.

Provides a top-level health endpoint that reports the status of both this
service and the connected policy engine (OPA). Used by load balancers,
orchestrators, and the dashboard to determine service availability.

Tag: Health
"""

from fastapi import APIRouter, Depends

from app.adapters.opa_adapter import OpaAdapter
from app.config import settings
from app.core.dependencies import get_policy_engine
from app.models.responses import success_response

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Health check",
    description="Service and policy engine health status",
)
async def health_check(
    engine: OpaAdapter = Depends(get_policy_engine),
):
    """Return the health status of this service and the policy engine.

    Returns:
        JSONResponse: A success envelope containing ``data.service`` ("ok"),
        ``data.policy_engine`` ("ok" or "unreachable"), ``data.version``
        (application version string), and ``data.node`` (node identifier).
        The top-level message indicates whether the service is fully healthy
        or degraded.
    """
    opa_ok = await engine.health_check()
    return success_response(
        data={
            "service": "ok",
            "policy_engine": "ok" if opa_ok else "unreachable",
            "version": settings.app_version,
            "node": settings.node_name,
        },
        message=(
            "Service is healthy"
            if opa_ok
            else "Service degraded: policy engine unreachable"
        ),
    )
