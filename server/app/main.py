"""
Policy Engine — FastAPI Application Factory.

Standalone policy-as-code microservice.
Integrated services call POST /api/v1/policies/evaluate to get permissions.

The dashboard/UI lives in a separate repo: ds-policy-engine-ui.
"""

import asyncio
import logging
import pathlib
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.settings import settings
from app.core.exceptions import PolicyEngineError
from app.database import close_db, init_db
from app.rest_api.response import error_response
from app.rest_api.routes import (
    db_viewer,
    decision_matrix,
    health,
    opa_management,
    opa_proxy,
    policy,
    rules,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("policy_engine")


# ---------------------------------------------------------------------------
# Lifespan — startup/shutdown
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database, seed data, and deploy policies on startup."""
    logger.info("Policy Engine starting (v%s)...", settings.app_version)

    # --- Database initialization ---
    session_factory = await init_db(settings.database_url)

    # Seed from JSON if database is empty (first run)
    from app.migrate_db import seed_from_json

    seed_path = pathlib.Path(settings.policies_dir) / "seed_rules.json"
    seeded = await seed_from_json(session_factory, str(seed_path))
    if seeded:
        logger.info("Seeded %d rules into database", seeded)

    # --- Wait for OPA to be ready ---
    from app.rest_api.depends import get_policy_deployer_usecase, get_policy_engine

    engine = get_policy_engine()
    for attempt in range(30):
        if await engine.health_check():
            logger.info("Policy engine (OPA) is ready")
            break
        logger.info("Waiting for policy engine... (attempt %d/30)", attempt + 1)
        await asyncio.sleep(1)
    else:
        logger.error("Policy engine not ready after 30s — starting without policies")
        yield
        await close_db()
        return

    # Deploy seed policies
    deployer = get_policy_deployer_usecase()
    await deployer.startup_deploy()
    logger.info("Policy Engine ready")

    yield

    # --- Shutdown ---
    await close_db()
    logger.info("Policy Engine shutting down")


# ---------------------------------------------------------------------------
# App creation
# ---------------------------------------------------------------------------

_docs_kwargs = (
    {"docs_url": "/docs", "redoc_url": "/redoc", "openapi_url": "/openapi.json"}
    if settings.docs_enabled
    else {"docs_url": None, "redoc_url": None, "openapi_url": None}
)

app = FastAPI(
    title="Policy Engine",
    description=(
        "Standalone policy-as-code microservice. "
        "Evaluates user permissions based on role and institute using OPA."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    **_docs_kwargs,
)

# --- CORS from environment ---
_cors_origins = settings.cors_origins_list
if _cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# ---------------------------------------------------------------------------
# Exception handlers — unified error responses
# ---------------------------------------------------------------------------


@app.exception_handler(PolicyEngineError)
async def policy_engine_error_handler(request: Request, exc: PolicyEngineError):
    """Handle all custom policy engine exceptions."""
    details = []
    if hasattr(exc, "field") and exc.field:
        details.append(
            {
                "field": exc.field,
                "value": getattr(exc, "value", ""),
                "reason": exc.message,
            }
        )
    if hasattr(exc, "rule_id"):
        details.append(
            {
                "field": "rule_id",
                "value": exc.rule_id,
                "reason": exc.message,
            }
        )
    if hasattr(exc, "existing_rule_id") and exc.existing_rule_id:
        details.append(
            {
                "field": "existing_rule_id",
                "value": exc.existing_rule_id,
                "reason": exc.message,
            }
        )

    body = error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        details=details if details else [{"field": "general", "reason": exc.message}],
    )
    return JSONResponse(status_code=exc.status_code, content=body)


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions."""
    logger.exception("Unhandled exception: %s", exc)
    body = error_response(
        code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        status_code=500,
        details=[{"field": "general", "reason": str(exc)}],
    )
    return JSONResponse(status_code=500, content=body)


# ---------------------------------------------------------------------------
# Register routers
# ---------------------------------------------------------------------------

app.include_router(policy.router)
app.include_router(rules.router)
app.include_router(decision_matrix.router)
app.include_router(opa_management.router)
app.include_router(db_viewer.router)
app.include_router(opa_proxy.router)
app.include_router(health.router)
