"""
Dependency injection wiring for FastAPI.

THIS IS THE SINGLE PLACE to swap implementations:
  - OPA -> Cedar: change get_policy_engine()
  - JSON -> Database: change get_rule_repository()
  - Permission-based -> RBAC: change get_rego_strategy()
"""

from functools import lru_cache

from app.adapters.opa_adapter import OpaAdapter
from app.config import settings
from app.repositories.sqlite_rule_repository import SqliteRuleRepository
from app.services.decision_matrix import DecisionMatrixService
from app.services.policy_deployer import PolicyDeployerService
from app.services.policy_evaluation import PolicyEvaluationService
from app.services.rego_generator import (
    PermissionBasedRegoStrategy,
    RegoGenerationStrategy,
)
from app.services.rule_management import RuleManagementService

# --- Adapter layer ---


@lru_cache
def get_policy_engine() -> OpaAdapter:
    """Get the policy engine adapter. Swap here to switch engines.

    Returns:
        OpaAdapter: Cached singleton adapter for communicating with OPA.
    """
    return OpaAdapter(settings)


def get_rule_repository() -> SqliteRuleRepository:
    """Get the rule repository. Swap here to switch storage.

    Reads ``async_session_factory`` at call time (after ``init_db`` has run).
    In tests, this function is overridden with an ``InMemoryRuleRepository``.

    Returns:
        SqliteRuleRepository: Repository instance backed by the current
        async session factory.
    """
    from app.db import get_session_factory

    return SqliteRuleRepository(get_session_factory())


@lru_cache
def get_rego_strategy() -> RegoGenerationStrategy:
    """Get the Rego generation strategy. Swap here for RBAC/ABAC.

    Returns:
        RegoGenerationStrategy: Cached singleton strategy instance (currently
        ``PermissionBasedRegoStrategy``).
    """
    return PermissionBasedRegoStrategy()


# --- Service layer ---


def get_policy_evaluation_service() -> PolicyEvaluationService:
    """Build a PolicyEvaluationService wired to the current policy engine.

    Returns:
        PolicyEvaluationService: Service instance for evaluating user permissions.
    """
    return PolicyEvaluationService(engine=get_policy_engine())


def get_rule_management_service() -> RuleManagementService:
    """Build a RuleManagementService wired to the current rule repository.

    Returns:
        RuleManagementService: Service instance for CRUD operations on rules.
    """
    return RuleManagementService(repository=get_rule_repository())


def get_policy_deployer_service() -> PolicyDeployerService:
    """Build a PolicyDeployerService with engine, repository, and strategy.

    Returns:
        PolicyDeployerService: Service instance for generating and deploying
        Rego policies to the policy engine.
    """
    return PolicyDeployerService(
        engine=get_policy_engine(),
        repository=get_rule_repository(),
        rego_strategy=get_rego_strategy(),
    )


def get_decision_matrix_service() -> DecisionMatrixService:
    """Build a DecisionMatrixService wired to the engine and repository.

    Returns:
        DecisionMatrixService: Service instance for building the role-permission
        decision matrix.
    """
    return DecisionMatrixService(
        engine=get_policy_engine(), repository=get_rule_repository()
    )
