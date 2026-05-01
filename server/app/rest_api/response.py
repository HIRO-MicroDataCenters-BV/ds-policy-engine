"""
Unified API response models.
Every endpoint returns the same envelope structure.
"""

from typing import Any, Literal

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field

from app.settings import settings


class ErrorItem(BaseModel):
    field: str
    value: str | None = None
    reason: str


class ErrorBody(BaseModel):
    code: str
    details: list[ErrorItem] = Field(default_factory=list)


class ResponseMetadata(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    request_id: str = Field(default_factory=lambda: f"req-{uuid4().hex[:8]}")
    version: str = Field(default=settings.app_version)


class ApiResponse(BaseModel):
    status: Literal["success", "error"]
    status_code: int
    message: str
    data: Any = None
    error: ErrorBody | None = None
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
) -> dict:
    """Build a standardized success response dict."""
    return ApiResponse(
        status="success",
        status_code=status_code,
        message=message,
        data=data,
        error=None,
    ).model_dump(mode="json")


def error_response(
    code: str,
    message: str,
    status_code: int = 400,
    details: list[dict] | None = None,
) -> dict:
    """Build a standardized error response dict."""
    error_items = [ErrorItem(**d) for d in (details or [])]
    return ApiResponse(
        status="error",
        status_code=status_code,
        message=message,
        data=None,
        error=ErrorBody(code=code, details=error_items),
    ).model_dump(mode="json")
