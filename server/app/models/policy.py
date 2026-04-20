"""
Pydantic models for policy evaluation requests and responses.
"""

from pydantic import BaseModel, Field


class PolicyEvaluationRequest(BaseModel):
    """Request body for evaluating a user's permissions against the deployed policy.

    The fields identify the user whose permissions should be resolved by
    the policy engine. The ``role`` field is the primary input used by the
    Rego policy to determine the granted permission set.
    """

    name: str = Field(..., min_length=1, description="User's full name")
    email: str = Field(..., min_length=1, description="User's email address")
    role: str = Field(
        ...,
        min_length=1,
        description="User's role (catalog_owner, catalog_creator, catalog_consumer)",
    )
    institute: str = Field(..., min_length=1, description="User's institute identifier")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "John Doe",
                    "email": "user@example.nl",
                    "role": "catalog_owner",
                    "institute": "local",
                }
            ]
        }
    }


class PolicyEvaluationResult(BaseModel):
    """Result of a policy evaluation containing the resolved permissions.

    Returned by the policy engine after evaluating the input against the
    currently deployed Rego policy. An empty ``permissions`` list indicates
    the role has no granted permissions (or no matching rule was found).
    """

    permissions: list[str] = []
