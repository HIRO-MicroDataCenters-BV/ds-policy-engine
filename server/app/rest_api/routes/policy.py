"""
Policy evaluation and deployment routes.

Tag: Policy Evaluation
"""

import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.usecases import (
    PolicyDeployerUsecase,
    PolicyEvaluationUsecase,
    RuleManagementUsecase,
)
from app.rest_api.depends import (
    get_policy_deployer_usecase,
    get_policy_evaluation_usecase,
    get_rule_management_usecase,
)
from app.rest_api.response import success_response
from app.rest_api.serializers import PolicyEvaluationRequest

logger = logging.getLogger("policy_engine.routes.policy")

router = APIRouter(prefix="/api/v1/policies", tags=["Policy Evaluation"])


class DeployRequest(BaseModel):
    """Optional body for deploy — includes deployer name."""

    deployed_by: str = "system"


class PreviewRequest(BaseModel):
    """Optional body for the preview endpoint.

    When ``rules`` is provided the Rego is generated from those rules
    instead of the saved manifest — useful for live-previewing unsaved
    edits in the Policy Builder.
    """

    rules: list[dict] | None = None


@router.post(
    "/evaluate",
    summary="Evaluate policy",
    description="Evaluate user permissions based on role and institute",
)
async def evaluate_policy(
    request: PolicyEvaluationRequest,
    service: PolicyEvaluationUsecase = Depends(get_policy_evaluation_usecase),
):
    """Evaluate a user's permissions based on their role and institute."""
    logger.debug("POST /evaluate role=%s institute=%s", request.role, request.institute)
    result = await service.evaluate(request)
    return success_response(data=result, message="Policy evaluated successfully")


@router.post(
    "/deploy",
    summary="Deploy policies to Policy Agent",
    description="Generate Rego and push to the policy agent",
)
async def deploy_policies(
    body: DeployRequest | None = None,
    service: PolicyDeployerUsecase = Depends(get_policy_deployer_usecase),
):
    """Full deploy: generate Rego from saved rules, push to Policy Agent, update manifest."""
    deployed_by = body.deployed_by if body else "system"
    result = await service.deploy(deployed_by=deployed_by)
    return success_response(data=result, message="Policies deployed successfully")


@router.post(
    "/preview",
    summary="Preview generated Rego",
    description="Preview Rego from saved rules, or pass custom rules in the body for live preview",
)
async def preview_rego(
    body: PreviewRequest | None = None,
    service: PolicyDeployerUsecase = Depends(get_policy_deployer_usecase),
):
    """Generate a Rego preview without deploying.

    If ``rules`` is provided in the request body, those rules are used
    for generation (live editor preview).  Otherwise the saved manifest
    rules are used.
    """
    rules = body.rules if body and body.rules is not None else None
    rego = await service.preview(rules=rules)
    return success_response(data={"rego": rego}, message="Rego preview generated")


@router.get(
    "/deploy-history",
    summary="Deploy history",
    description="Returns the recent deploy history log",
)
async def deploy_history(
    service: PolicyDeployerUsecase = Depends(get_policy_deployer_usecase),
):
    """Retrieve the most recent deploy history entries."""
    history = await service.get_deploy_history()
    return success_response(
        data={"history": history}, message="Deploy history retrieved"
    )


@router.get(
    "/overview",
    summary="Policy manager overview",
    description="Stats, conflicts, and deploy info for the manager dashboard",
)
async def policy_overview(
    deployer: PolicyDeployerUsecase = Depends(get_policy_deployer_usecase),
    rule_svc: RuleManagementUsecase = Depends(get_rule_management_usecase),
):
    """Build an overview with stats, conflicts, and deploy info."""
    meta = await rule_svc.get_meta()
    rules = meta.get("rule_scenarios", [])
    all_roles = meta.get("roles", [])
    all_perms = meta.get("permissions", [])
    all_institutes = meta.get("institutes", [])

    # Get manifest for last_deployed
    manifest = await deployer._repo.get_manifest()
    last_deployed = manifest.get("last_deployed")
    all_rules = manifest.get("rules", [])
    enabled_count = len([r for r in all_rules if r.get("enabled", True)])
    disabled_count = len(all_rules) - enabled_count

    # Detect conflicts: same role+institute with different permission sets
    conflicts = []
    pair_map = {}
    for r in all_rules:
        if not r.get("enabled", True):
            continue
        key = (r.get("role", ""), r.get("institute", ""))
        perms = tuple(sorted(r.get("permissions", [])))
        if key in pair_map:
            if pair_map[key]["perms"] != perms:
                conflicts.append(
                    {
                        "type": "permission_mismatch",
                        "role": key[0],
                        "institute": key[1],
                        "rule_a": pair_map[key]["name"],
                        "rule_b": r.get("name", ""),
                        "message": f"Rules '{pair_map[key]['name']}' and '{r.get('name', '')}' have the same role+institute but different permissions",
                    }
                )
        else:
            pair_map[key] = {"name": r.get("name", ""), "perms": perms}

    # Detect warnings
    warnings = []
    if disabled_count > 0:
        disabled_names = [
            r.get("name", r.get("id", "?"))
            for r in all_rules
            if not r.get("enabled", True)
        ]
        warnings.append(
            {
                "type": "disabled_rules",
                "count": disabled_count,
                "message": f"{disabled_count} rule(s) disabled and won't be enforced: {', '.join(disabled_names)}",
            }
        )
    # Roles with no permissions
    for r in all_rules:
        if r.get("enabled", True) and not r.get("permissions"):
            warnings.append(
                {
                    "type": "empty_permissions",
                    "rule": r.get("name", ""),
                    "message": f"Rule '{r.get('name', '')}' has no permissions assigned",
                }
            )

    # Deploy history
    history = await deployer.get_deploy_history()

    return success_response(
        data={
            "stats": {
                "total_rules": len(all_rules),
                "enabled_rules": enabled_count,
                "disabled_rules": disabled_count,
                "roles": len(all_roles),
                "institutes": len(all_institutes),
                "permissions": len(all_perms),
                "last_deployed": last_deployed,
            },
            "conflicts": conflicts,
            "warnings": warnings,
            "deploy_history": history[:10],
        }
    )
