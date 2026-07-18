class GoalUnderstandingError(Exception):
    """Base exception for Goal Understanding module."""
    pass

class InvalidLLMResponseError(GoalUnderstandingError):
    """Raised when the LLM response is missing, empty, or unparseable JSON."""
    pass

class GoalValidationError(GoalUnderstandingError):
    """Raised when the parsed JSON fails Pydantic business logic validation (e.g. negative budget)."""
    pass

class PromptInjectionDetectedError(GoalUnderstandingError):
    """Raised when a prompt injection attempt is detected in the query."""
    pass
