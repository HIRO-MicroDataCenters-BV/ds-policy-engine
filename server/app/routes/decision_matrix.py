"""
Decision matrix route.

Exposes an endpoint that builds a live decision matrix showing the resolved
permissions for every known role. The matrix is computed by querying the
policy engine for each role defined in the rule repository.

Tag: Decision Matrix
"""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_decision_matrix_service
from app.models.responses import success_response
from app.services.decision_matrix import DecisionMatrixService

router = APIRouter(prefix="/api/v1", tags=["Decision Matrix"])


@router.get(
    "/decision-matrix",
    summary="Get decision matrix",
    description="Live decision matrix showing permissions for every role",
)
async def get_decision_matrix(
    service: DecisionMatrixService = Depends(get_decision_matrix_service),
):
    """Build and return the live decision matrix for all roles.

    The matrix cross-references every role against every known permission,
    showing which permissions each role is granted by the currently deployed
    policy.

    Returns:
        JSONResponse: A success envelope containing the matrix data structure
        with roles, permissions, and their intersections.
    """
    result = await service.build_matrix()
    return success_response(data=result, message="Decision matrix generated")
