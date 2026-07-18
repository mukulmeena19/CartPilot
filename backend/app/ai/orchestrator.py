import json
import structlog
from typing import AsyncGenerator
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.ai.understanding.service import GoalUnderstandingService
from app.ai.understanding.schemas import GoalUnderstandingRequest
from app.ai.planning.service import PlanningService
from app.ai.planning.schemas import PlanningRequest
from app.ai.retrieval.service import RetrievalService
from app.ai.verification.service import VerificationService
from app.ai.verification.schemas import VerificationRequest
from app.ai.memory.service import MemoryService
from app.ai.optimization.service import OptimizationService
from app.ai.explainability.service import ExplainabilityService

logger = structlog.get_logger(__name__)

class PipelineOrchestrator:
    def __init__(self):
        self.understanding = GoalUnderstandingService()
        self.planning = PlanningService()
        self.retrieval = RetrievalService()
        self.verification = VerificationService()
        self.memory = MemoryService()
        self.optimization = OptimizationService()
        self.explainability = ExplainabilityService()

    def _format_sse(self, event: str, data: dict = None) -> str:
        """Formats a Server-Sent Event."""
        payload = {"stage": event}
        if data:
            payload.update(data)
        return f"data: {json.dumps(payload)}\n\n"

    async def generate_cart_stream(self, query: str, user: User, db: Session) -> AsyncGenerator[str, None]:
        """
        Executes the entire 7-stage AI Pipeline sequentially, yielding SSE progress markers.
        """
        try:
            # 1. UNDERSTANDING
            yield self._format_sse("UNDERSTANDING")
            goal_req = GoalUnderstandingRequest(query=query)
            goal_context, _ = self.understanding.understand_goal(goal_req)
            
            # 2. PLANNING
            yield self._format_sse("PLANNING")
            plan_req = PlanningRequest(goal_context=goal_context)
            shopping_plan, _ = self.planning.create_shopping_plan(plan_req)
            
            # 3. RETRIEVAL
            yield self._format_sse("RETRIEVAL")
            retrieval_result, _ = self.retrieval.retrieve_candidates(shopping_plan, db)
            
            # 4. VERIFICATION
            yield self._format_sse("VERIFICATION")
            verification_req = VerificationRequest(candidates=retrieval_result)
            verification_result, _ = self.verification.verify_candidates(verification_req, db)
            
            # 5. MEMORY
            yield self._format_sse("MEMORY")
            # For simplicity, extract preferences from user JSONB column
            preferences, _ = self.memory.get_preferences(user.id, db)
            
            # 6. OPTIMIZATION
            yield self._format_sse("OPTIMIZATION")
            optimized_plan, _ = self.optimization.optimize_cart(shopping_plan, verification_result, preferences)
            
            # 7. EXPLAINABILITY
            yield self._format_sse("EXPLAINABILITY")
            explainable_plan, _ = self.explainability.explain_plan(optimized_plan)
            
            # 8. COMPLETE
            # Return the final explainable plan in the COMPLETE event
            yield self._format_sse("COMPLETE", {"cart": explainable_plan.model_dump()})
            
        except Exception as e:
            logger.error("Pipeline Orchestrator failed", error=str(e), exc_info=True)
            yield self._format_sse("ERROR", {"message": str(e)})
