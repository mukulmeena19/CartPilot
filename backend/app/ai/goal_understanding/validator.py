from app.ai.goal_understanding.models import GoalContext
from app.ai.exceptions import GoalValidationError, PromptInjectionDetectedError

class GoalValidator:
    @staticmethod
    def validate(goal: GoalContext) -> GoalContext:
        """
        Enforces strict business rules on the parsed LLM output.
        """
        if goal.confidence < 0.3:
            raise GoalValidationError("Confidence is too low. The request is ambiguous or invalid.")
        
        if goal.budget is not None and goal.budget <= 0:
            raise GoalValidationError("Budget must be a positive number.")
            
        if goal.people is not None and (goal.people < 1 or goal.people > 100):
            raise GoalValidationError("Number of people must be between 1 and 100.")
            
        # Basic prompt injection heuristc check on the output
        suspicious_keywords = ["ignore previous instructions", "system prompt", "bypass"]
        if any(keyword in goal.shopping_goal.lower() for keyword in suspicious_keywords):
            raise PromptInjectionDetectedError("Detected malicious intent in the parsed goal.")
            
        return goal
