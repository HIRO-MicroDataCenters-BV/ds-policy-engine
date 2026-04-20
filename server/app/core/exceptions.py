"""
Custom exception hierarchy for the policy engine.
Each exception maps to a specific HTTP status code and error code.
"""


class PolicyEngineError(Exception):
    """Base exception for all policy engine errors."""

    def __init__(
        self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class PolicyEngineUnreachableError(PolicyEngineError):
    """OPA or policy engine is not available."""

    def __init__(self, message: str = "Policy engine is not available"):
        super().__init__(message, code="POLICY_ENGINE_UNREACHABLE", status_code=503)


class PolicyEvaluationError(PolicyEngineError):
    """Error during policy evaluation."""

    def __init__(self, message: str = "Policy evaluation failed"):
        super().__init__(message, code="POLICY_EVALUATION_ERROR", status_code=500)


class RuleNotFoundError(PolicyEngineError):
    """Requested rule does not exist."""

    def __init__(self, rule_id: str):
        self.rule_id = rule_id
        super().__init__(
            message=f"Rule with id '{rule_id}' not found",
            code="RULE_NOT_FOUND",
            status_code=404,
        )


class RuleValidationError(PolicyEngineError):
    """Rule data fails validation."""

    def __init__(self, message: str, field: str = "", value: str = ""):
        self.field = field
        self.value = value
        super().__init__(message, code="VALIDATION_ERROR", status_code=400)


class RuleConflictError(PolicyEngineError):
    """Duplicate or conflicting rule."""

    def __init__(self, message: str, existing_rule_id: str = ""):
        self.existing_rule_id = existing_rule_id
        super().__init__(message, code="RULE_CONFLICT", status_code=409)


class PolicyDeploymentError(PolicyEngineError):
    """Failed to deploy policy to engine."""

    def __init__(self, message: str = "Policy deployment failed"):
        super().__init__(message, code="POLICY_DEPLOYMENT_ERROR", status_code=500)
