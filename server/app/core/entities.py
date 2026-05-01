"""
Domain entities.

Policy-engine is simple enough today that the single Pydantic representation
in ``app.rest_api.serializers`` doubles as both the HTTP schema and the
domain entity. This module exists to (a) be the natural home for future
domain types that diverge from the HTTP shape (e.g. pure-dataclass models
for complex invariants, DDD value objects) and (b) match the ds-catalog
folder convention.

Right now we re-export the HTTP schemas as the domain representation so
code paths in ``app.core.*`` don't need to import from ``app.rest_api``.
When a real split becomes useful, replace the re-exports with first-class
entity definitions and let the HTTP serializers map to them explicitly.
"""

from app.rest_api.serializers import (
    PaginationMeta,
    PaginationParams,
    PolicyEvaluationRequest,
    PolicyEvaluationResult,
    RuleCreate,
    RuleResponse,
    RuleUpdate,
)

__all__ = [
    "PaginationMeta",
    "PaginationParams",
    "PolicyEvaluationRequest",
    "PolicyEvaluationResult",
    "RuleCreate",
    "RuleResponse",
    "RuleUpdate",
]
