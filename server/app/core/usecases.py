"""
Business use cases.

Every cross-boundary workflow in the service is expressed here as an
interface (``I...Usecase``) plus a concrete implementation. Routes
(``app.rest_api.routes``) depend on the interfaces; the DI wiring in
``app.rest_api.depends`` picks the implementation at startup. This is the
only place business logic orchestrates repositories, validators, adapters,
and the Rego strategy — routes do not.

Pattern lifted from ``ds-catalog/server/app/core/usecases.py``.
"""

import logging
import math
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from app.core.policy_engine import PolicyEngine
from app.core.entities import (
    PaginationMeta,
    PaginationParams,
    PolicyEvaluationRequest,
    RuleCreate,
    RuleUpdate,
)
from app.core.exceptions import (
    PolicyDeploymentError,
    RuleConflictError,
    RuleNotFoundError,
)
from app.core.rego_generator import RegoGenerationStrategy
from app.core.repository.repositories import RuleRepository
from app.core.validators import validate_permissions, validate_role

logger = logging.getLogger("policy_engine.usecases")


# ---------------------------------------------------------------------------
# Interfaces
# ---------------------------------------------------------------------------


class IRuleManagementUsecase(ABC):
    """CRUD + discovery operations on the rule set."""

    @abstractmethod
    async def list_rules(
        self, params: PaginationParams
    ) -> tuple[list[dict], PaginationMeta]: ...

    @abstractmethod
    async def get_rule(self, rule_id: str) -> dict: ...

    @abstractmethod
    async def create_rule(self, data: RuleCreate) -> dict: ...

    @abstractmethod
    async def update_rule(self, rule_id: str, data: RuleUpdate) -> dict: ...

    @abstractmethod
    async def delete_rule(self, rule_id: str) -> None: ...

    @abstractmethod
    async def toggle_rule(self, rule_id: str) -> dict: ...

    @abstractmethod
    async def get_known_roles(self) -> list[str]: ...

    @abstractmethod
    async def get_known_permissions(self) -> list[str]: ...

    @abstractmethod
    async def get_meta(self) -> dict: ...


class IPolicyEvaluationUsecase(ABC):
    """Evaluate a policy for a given user's role + institute."""

    @abstractmethod
    async def evaluate(self, request: PolicyEvaluationRequest) -> dict: ...


class IPolicyDeployerUsecase(ABC):
    """Compile the current rule set to Rego and push to the policy engine."""

    @abstractmethod
    async def deploy(self, deployed_by: str = "system") -> dict: ...

    @abstractmethod
    async def get_deploy_history(self, limit: int = 20) -> list[dict]: ...

    @abstractmethod
    async def preview(self, rules: list[dict] | None = None) -> str: ...

    @abstractmethod
    async def startup_deploy(self) -> bool: ...


class IDecisionMatrixUsecase(ABC):
    """Build a live role × permission decision matrix."""

    @abstractmethod
    async def build_matrix(self) -> dict: ...


# ---------------------------------------------------------------------------
# Implementations
# ---------------------------------------------------------------------------


class RuleManagementUsecase(IRuleManagementUsecase):
    """Default rule-management implementation backed by a ``RuleRepository``."""

    def __init__(self, repository: RuleRepository):
        self._repo = repository

    async def list_rules(
        self, params: PaginationParams
    ) -> tuple[list[dict], PaginationMeta]:
        all_rules = await self._repo.list_rules()

        if params.role:
            all_rules = [r for r in all_rules if r.get("role") == params.role]
        if params.enabled is not None:
            all_rules = [
                r for r in all_rules if r.get("enabled", True) == params.enabled
            ]
        if params.search:
            q = params.search.lower()
            all_rules = [r for r in all_rules if q in r.get("name", "").lower()]

        reverse = params.sort_order == "desc"
        all_rules.sort(key=lambda r: r.get(params.sort_by, ""), reverse=reverse)

        total_items = len(all_rules)
        total_pages = max(1, math.ceil(total_items / params.page_size))
        start = (params.page - 1) * params.page_size
        end = start + params.page_size
        page_rules = all_rules[start:end]

        pagination = PaginationMeta(
            page=params.page,
            page_size=params.page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_previous=params.page > 1,
        )
        return page_rules, pagination

    async def get_rule(self, rule_id: str) -> dict:
        rule = await self._repo.get_rule(rule_id)
        if not rule:
            raise RuleNotFoundError(rule_id)
        return rule

    async def create_rule(self, data: RuleCreate) -> dict:
        validate_role(data.role)
        validate_permissions(data.permissions)

        existing = await self._repo.list_rules()
        for r in existing:
            if r.get("name", "").lower() == data.name.lower():
                raise RuleConflictError(
                    message=f"A rule named '{data.name}' already exists",
                    existing_rule_id=r["id"],
                )

        rule_data = data.model_dump()
        rule = await self._repo.create_rule(rule_data)
        logger.info("Created rule '%s' (%s)", rule["name"], rule["id"])
        return rule

    async def update_rule(self, rule_id: str, data: RuleUpdate) -> dict:
        updates = data.model_dump(exclude_none=True)
        if "role" in updates:
            validate_role(updates["role"])
        if "permissions" in updates:
            validate_permissions(updates["permissions"])

        result = await self._repo.update_rule(rule_id, updates)
        if not result:
            raise RuleNotFoundError(rule_id)
        logger.info("Updated rule '%s'", rule_id)
        return result

    async def delete_rule(self, rule_id: str) -> None:
        deleted = await self._repo.delete_rule(rule_id)
        if not deleted:
            raise RuleNotFoundError(rule_id)
        logger.info("Deleted rule '%s'", rule_id)

    async def toggle_rule(self, rule_id: str) -> dict:
        rule = await self._repo.get_rule(rule_id)
        if not rule:
            raise RuleNotFoundError(rule_id)
        new_state = not rule.get("enabled", True)
        result = await self._repo.update_rule(rule_id, {"enabled": new_state})
        # Rule was there when we read it but is gone now — treat as not found
        # rather than propagating None and crashing callers that expect a dict.
        if result is None:
            raise RuleNotFoundError(rule_id)
        logger.info("Toggled rule '%s' -> enabled=%s", rule_id, new_state)
        return result

    async def get_known_roles(self) -> list[str]:
        rules = await self._repo.list_rules()
        return sorted({r.get("role") for r in rules if r.get("role")})

    async def get_known_permissions(self) -> list[str]:
        rules = await self._repo.list_rules()
        perms: set[str] = set()
        for r in rules:
            perms.update(r.get("permissions", []))
        return sorted(perms)

    async def get_meta(self) -> dict:
        rules = await self._repo.list_rules()
        roles = sorted({r.get("role") for r in rules if r.get("role")})
        institutes = sorted({r.get("institute") for r in rules if r.get("institute")})
        perms: set[str] = set()
        # Collect unique (role, institute) pairs across ALL rules (enabled or
        # disabled) — the Tester dropdowns need to show disabled scenarios so
        # users can preview what enabling the rule would do. If the UI wants
        # only enabled scenarios later, add an explicit filter here.
        role_institute_pairs: list[dict] = []
        seen_pairs: set[tuple[str, str]] = set()
        for r in rules:
            perms.update(r.get("permissions", []))
            role = r.get("role", "")
            inst = r.get("institute", "")
            if role and inst and (role, inst) not in seen_pairs:
                seen_pairs.add((role, inst))
                role_institute_pairs.append(
                    {"role": role, "institute": inst, "name": r.get("name", "")}
                )
        return {
            "roles": roles,
            "institutes": institutes,
            "permissions": sorted(perms),
            "rule_scenarios": sorted(role_institute_pairs, key=lambda x: x["role"]),
        }


class PolicyEvaluationUsecase(IPolicyEvaluationUsecase):
    """Delegates the actual decision to the configured ``PolicyEngine`` adapter."""

    def __init__(self, engine: PolicyEngine):
        self._engine = engine

    async def evaluate(self, request: PolicyEvaluationRequest) -> dict:
        input_data = {
            "name": request.name,
            "email": request.email,
            "role": request.role,
            "institute": request.institute,
        }
        logger.info("Evaluating: role=%s institute=%s", request.role, request.institute)
        logger.debug("Evaluation input: %s", input_data)

        result = await self._engine.evaluate(input_data)
        permissions = result.get("permissions", [])
        logger.info("Decision: role=%s permissions=%d", request.role, len(permissions))
        logger.debug("Granted: %s", permissions)
        return {"permissions": permissions}


class PolicyDeployerUsecase(IPolicyDeployerUsecase):
    """Compiles the rule set to Rego and pushes to the policy engine."""

    def __init__(
        self,
        engine: PolicyEngine,
        repository: RuleRepository,
        rego_strategy: RegoGenerationStrategy,
    ):
        self._engine = engine
        self._repo = repository
        self._strategy = rego_strategy

    async def deploy(self, deployed_by: str = "system") -> dict:
        manifest = await self._repo.get_manifest()
        rules = manifest.get("rules", [])

        rego = self._strategy.generate(rules)
        pushed = await self._engine.push_policy("ds_authz", rego)
        if not pushed:
            raise PolicyDeploymentError("Failed to push policy to engine")

        deployed_at = datetime.now(timezone.utc).isoformat()
        manifest["last_deployed"] = deployed_at
        await self._repo.save_manifest(manifest)

        enabled_rules = [r for r in rules if r.get("enabled", True)]
        history_entry = {
            "deployed_at": deployed_at,
            "deployed_by": deployed_by,
            "rules_count": len(enabled_rules),
            "roles": sorted({r.get("role") for r in enabled_rules if r.get("role")}),
        }
        version = None
        try:
            result = await self._repo.append_deploy_history(history_entry)
            version = result.get("version")
        except Exception:
            logger.warning("Failed to save deploy history", exc_info=True)

        logger.info("Policy deployed successfully (v%s by %s)", version, deployed_by)
        return {
            "deployed_at": deployed_at,
            "rego": rego,
            "rules_count": len(enabled_rules),
            "version": version,
            "deployed_by": deployed_by,
        }

    async def get_deploy_history(self, limit: int = 20) -> list[dict]:
        return await self._repo.get_deploy_history(limit=limit)

    async def preview(self, rules: list[dict] | None = None) -> str:
        if rules is None:
            manifest = await self._repo.get_manifest()
            rules = manifest.get("rules", [])
        return self._strategy.generate(rules)

    async def startup_deploy(self) -> bool:
        manifest = await self._repo.get_manifest()
        rules = manifest.get("rules", [])
        if not rules:
            logger.info("No rules to deploy on startup")
            return True

        rego = self._strategy.generate(rules)
        pushed = await self._engine.push_policy("ds_authz", rego)
        logger.info("Startup deploy: pushed=%s, rules=%d", pushed, len(rules))
        return pushed


class DecisionMatrixUsecase(IDecisionMatrixUsecase):
    """Builds the live role × permission grid by querying the engine."""

    def __init__(self, engine: PolicyEngine, repository: RuleRepository):
        self._engine = engine
        self._repo = repository

    async def build_matrix(self) -> dict:
        rules = await self._repo.list_rules()
        roles = sorted({r.get("role") for r in rules if r.get("role")})
        all_perms: set[str] = set()
        for r in rules:
            all_perms.update(r.get("permissions", []))
        all_perms_sorted = sorted(all_perms)

        # Build role -> institute mapping from rules so we query OPA with the
        # correct institute for each role (a role may appear under multiple
        # institutes, so we collect all unique (role, institute) pairs).
        role_institute_pairs: list[tuple[str, str, str]] = []
        seen_pairs: set[tuple[str, str]] = set()
        for r in rules:
            role = r.get("role", "")
            inst = r.get("institute", "")
            if role and (role, inst) not in seen_pairs:
                seen_pairs.add((role, inst))
                role_institute_pairs.append((role, inst, r.get("name", "")))

        logger.debug(
            "Building matrix: %d role-institute pairs x %d permissions",
            len(role_institute_pairs),
            len(all_perms_sorted),
        )

        matrix = []
        for role, institute, rule_name in role_institute_pairs:
            input_data = {
                "name": f"matrix-{role}",
                "email": f"{role}@test.local",
                "role": role,
                "institute": institute,
            }
            try:
                result = await self._engine.evaluate(input_data)
                permissions = result.get("permissions", [])
            except Exception:
                logger.warning(
                    "Matrix evaluation failed for role=%s institute=%s", role, institute
                )
                permissions = []

            entry: dict = {
                "role": role,
                "institute": institute,
                "permissions": permissions,
            }
            if rule_name:
                entry["rule_name"] = rule_name
            for perm in all_perms_sorted:
                key = perm.replace(":", "_").replace("-", "_")
                entry[key] = perm in permissions
            matrix.append(entry)

        return {
            "matrix": matrix,
            "roles": roles,
            "permissions": all_perms_sorted,
        }
