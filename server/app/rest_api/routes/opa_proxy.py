"""
OPA reverse proxy — exposes OPA under /opa/* on the same port.

All OPA endpoints become reachable through the Policy Engine service
so that only one port needs to be exposed:

    /opa/v1/data/...     →  OPA evaluate
    /opa/v1/policies/... →  OPA policy CRUD
    /opa/health          →  OPA health

Tag: OPA Proxy
"""

import logging

import httpx
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from app.rest_api.response import error_response
from app.settings import settings

logger = logging.getLogger("policy_engine.opa_proxy")

router = APIRouter(prefix="/opa", tags=["OPA Proxy"])


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    summary="OPA reverse proxy",
    description=(
        "Forwards any request to the OPA server. "
        "Use /opa/v1/data/... for evaluation, /opa/v1/policies for "
        "management, /opa/health for health."
    ),
    # Excluded from the OpenAPI schema — a single multi-method handler
    # generates duplicate operationIds that the openapi-generator-cli
    # rejects in strict mode. The proxy is a debug surface, not meant
    # for SDK consumers anyway.
    include_in_schema=False,
)
async def opa_proxy(path: str, request: Request):
    """Forward request to OPA and return the response."""
    target_url = f"{settings.opa_base_url}/{path}"

    # Forward query parameters
    if request.url.query:
        target_url += f"?{request.url.query}"

    body = await request.body()
    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in ("host", "connection", "transfer-encoding")
    }

    try:
        async with httpx.AsyncClient(timeout=settings.opa_timeout) as client:
            resp = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
            )
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                media_type=resp.headers.get("content-type", "application/json"),
            )
    except httpx.HTTPError as exc:
        logger.error("OPA proxy error: %s", exc)
        body = error_response(
            code="OPA_UNREACHABLE",
            message="OPA engine unreachable",
            status_code=502,
            details=[{"field": "general", "reason": str(exc)}],
        )
        return JSONResponse(status_code=502, content=body)
