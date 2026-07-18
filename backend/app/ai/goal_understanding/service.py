import structlog
from typing import Tuple, Dict, Any
from app.ai.providers import get_llm_provider
from app.ai.goal_understanding.parser import GoalParser
from app.ai.goal_understanding.validator import GoalValidator
from app.ai.goal_understanding.models import GoalContext
from app.ai.exceptions import GoalUnderstandingError

logger = structlog.get_logger(__name__)

class GoalUnderstandingService:
    def __init__(self):
        self.provider = get_llm_provider()
        self.parser = GoalParser(provider=self.provider)
        self.validator = GoalValidator()

    def understand_goal(self, query: str) -> Tuple[GoalContext, Dict[str, Any]]:
        logger.info("Starting goal understanding", query_length=len(query))
        
        try:
            # 1. Parse (LLM Execution)
            parsed_goal, metadata = self.parser.parse_query(query)
            
            # 2. Validate (Business Logic)
            validated_goal = self.validator.validate(parsed_goal)
            
            # Log observability metadata
            logger.info(
                "Goal understanding successful",
                model=metadata.get("model"),
                latency_sec=metadata.get("latency_sec"),
                total_tokens=metadata.get("total_tokens"),
                confidence=validated_goal.confidence
            )
            
            return validated_goal, metadata
            
        except GoalUnderstandingError as e:
            logger.warning("Goal understanding failed validation", error=str(e))
            raise
        except Exception as e:
            logger.error("Unexpected error in goal understanding", error=str(e))
            raise
