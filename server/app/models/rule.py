"""
Pydantic models for rule CRUD operations.
"""

from typing import Literal

from datetime import datetime

from pydantic import BaseModel, Field


class RuleCreate(BaseModel):
    """Schema for creating a new authorization rule.

    Defines the required and optional fields accepted when a client submits
    a request to create a rule. Each rule maps a role to a set of permissions.
    """

    name: str = Field(
        ..., min_length=1, max_length=100, description="Rule display name"
    )
    description: str = Field(default="", max_length=500)
    role: str = Field(..., description="Target role for this rule")
    institute: str = Field(default="", description="Institute this rule applies to")
    permissions: list[str] = Field(
        default_factory=list,
        description=(
            "Permissions granted by this rule. May be empty "
            "(the service surfaces such rules as a warning in the overview)."
        ),
    )
    enabled: bool = Field(default=True)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Catalog Owner Full Access",
                    "description": "Full permissions including cross-node capabilities",
                    "role": "catalog_owner",
                    "institute": "local",
                    "permissions": [
                        "catalog:read",
                        "catalog:create",
                        "catalog:update",
                        "catalog:delete",
                        "decentralized-search:execute",
                        "federated-learning:execute",
                    ],
                    "enabled": True,
                }
            ]
        }
    }


class RuleUpdate(BaseModel):
    """Schema for partially updating an existing rule.

    All fields are optional; only the supplied fields are modified. Omitted
    fields retain their current values.
    """

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    role: str | None = None
    institute: str | None = None
    permissions: list[str] | None = None
    enabled: bool | None = None


class RuleResponse(BaseModel):
    """Schema for a rule returned in API responses.

    Contains all persisted fields including server-generated values such as
    ``id``, ``created_at``, and ``updated_at``.
    """

    id: str
    name: str
    description: str = ""
    role: str
    institute: str = ""
    permissions: list[str]
    enabled: bool = True
    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseModel):
    """Query parameters for paginated rule listing.

    Supports page-based pagination, sorting by common columns, and optional
    filtering by role, enabled status, or a free-text search string.
    """

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=50)
    sort_by: Literal["created_at", "updated_at", "name", "role"] = "created_at"
    sort_order: Literal["asc", "desc"] = "desc"
    role: str | None = None
    enabled: bool | None = None
    search: str | None = None


class PaginationMeta(BaseModel):
    """Metadata describing a paginated result set.

    Returned alongside paginated data to allow clients to render pagination
    controls and determine whether additional pages exist.
    """

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool
