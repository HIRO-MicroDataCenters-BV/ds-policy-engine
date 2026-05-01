"""
Dependency injection wiring for FastAPI.

THIS IS THE SINGLE PLACE to swap implementations:
  - OPA -> Cedar: change get_policy_engine()
  - JSON -> Database: change get_rule_repository()
  - Permission-based -> RBAC: change get_rego_strategy()
"""

from functools import lru_cache

from app.core.opa_adapter import OpaAdapter
from app.settings import settings
from app.core.rego_generator import PermissionBasedRegoStrategy, RegoGenerationStrategy
from app.core.repository.sqlite_rule_repository import SqliteRuleRepository
from app.core.usecases import (
    DecisionMatrixUsecase,
    PolicyDeployerUsecase,
    PolicyEvaluationUsecase,
    RuleManagementUsecase,
)

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
    from app.database import get_session_factory

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


def get_policy_evaluation_usecase() -> PolicyEvaluationUsecase:
    """Build a PolicyEvaluationUsecase wired to the current policy engine.

    Returns:
        PolicyEvaluationUsecase: Service instance for evaluating user permissions.
    """
    return PolicyEvaluationUsecase(engine=get_policy_engine())


def get_rule_management_usecase() -> RuleManagementUsecase:
    """Build a RuleManagementUsecase wired to the current rule repository.

    Returns:
        RuleManagementUsecase: Service instance for CRUD operations on rules.
    """
    return RuleManagementUsecase(repository=get_rule_repository())


def get_policy_deployer_usecase() -> PolicyDeployerUsecase:
    """Build a PolicyDeployerUsecase with engine, repository, and strategy.

    Returns:
        PolicyDeployerUsecase: Service instance for generating and deploying
        Rego policies to the policy engine.
    """
    return PolicyDeployerUsecase(
        engine=get_policy_engine(),
        repository=get_rule_repository(),
        rego_strategy=get_rego_strategy(),
    )


def get_decision_matrix_usecase() -> DecisionMatrixUsecase:
    """Build a DecisionMatrixUsecase wired to the engine and repository.

    Returns:
        DecisionMatrixUsecase: Service instance for building the role-permission
        decision matrix.
    """
    return DecisionMatrixUsecase(
        engine=get_policy_engine(), repository=get_rule_repository()
    )
