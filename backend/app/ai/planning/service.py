import time
import structlog
from typing import Tuple, Dict, Any
from app.ai.providers import get_llm_provider
from app.ai.goal_understanding.models import GoalContext
from app.ai.planning.models import ShoppingPlan
from app.ai.planning.planner import Planner
from app.ai.exceptions import GoalUnderstandingError

logger = structlog.get_logger(__name__)

class PlanningService:
    def __init__(self):
        self.provider = get_llm_provider()
        self.planner = Planner(provider=self.provider)

    def plan_goal(self, goal: GoalContext) -> Tuple[ShoppingPlan, Dict[str, Any]]:
        start_time = time.time()
        logger.info("Starting planning generation", goal_type=goal.goal_type, budget=goal.budget)
        
        try:
            plan, metadata = self.planner.generate_plan(goal)
            
            total_latency = time.time() - start_time
            
            logger.info(
                "Planning successful",
                ai_latency_sec=metadata.get("latency_sec"),
                total_latency_sec=total_latency,
                rules_latency_sec=total_latency - metadata.get("latency_sec", 0),
                total_tokens=metadata.get("total_tokens"),
                planning_confidence=plan.planning_confidence
            )
            
            return plan, metadata
            
        except Exception as e:
            logger.error("Planning generation failed", error=str(e))
            raise
