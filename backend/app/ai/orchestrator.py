import json
import structlog
from typing import AsyncGenerator
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.ai.goal_understanding.service import GoalUnderstandingService
from app.ai.planning.service import PlanningService
from app.ai.retrieval.service import RetrievalService
from app.ai.verification.service import VerificationService
from app.ai.memory.service import MemoryService
from app.ai.optimization.service import OptimizationService
from app.ai.explainability.service import ExplainabilityService

logger = structlog.get_logger(__name__)

class PipelineOrchestrator:
    def __init__(self):
        # Instantiate services that do NOT need a DB session.
        self.understanding = GoalUnderstandingService()
        self.planning = PlanningService()
        self.optimization = OptimizationService()
        self.explainability = ExplainabilityService()

    def _format_sse(self, event: str, data: dict = None) -> str:
        payload = {"stage": event}
        if data:
            payload.update(data)
        return f"data: {json.dumps(payload)}\n\n"

    async def generate_cart_stream(self, query: str, user: User, db: Session) -> AsyncGenerator[str, None]:
        try:
            # Instantiate DB-dependent services
            retrieval = RetrievalService(db)
            verification = VerificationService(db)
            memory = MemoryService(db)

            # 1. UNDERSTANDING
            yield self._format_sse("UNDERSTANDING")
            goal_context, _ = self.understanding.understand_goal(query)
            
            # 2. PLANNING
            yield self._format_sse("PLANNING")
            shopping_plan, _ = self.planning.plan_goal(goal_context)
            
            # 3. RETRIEVAL
            yield self._format_sse("RETRIEVAL")
            retrieval_result, _ = retrieval.retrieve_products(shopping_plan)
            
            # 4. VERIFICATION
            yield self._format_sse("VERIFICATION")
            verification_result, _ = verification.verify(retrieval_result)
            
            # 5. MEMORY
            yield self._format_sse("MEMORY")
            preferences, _ = memory.get_user_preferences(user.id)
            
            # 6. OPTIMIZATION
            yield self._format_sse("OPTIMIZATION")
            optimized_plan, _ = self.optimization.optimize_cart(shopping_plan, verification_result, preferences)
            
            # 7. EXPLAINABILITY
            yield self._format_sse("EXPLAINABILITY")
            explainable_plan, _ = self.explainability.explain_plan(optimized_plan)
            
            # 8. COMPLETE
            yield self._format_sse("COMPLETE", {"cart": explainable_plan.model_dump()})
            
        except Exception as e:
            logger.error("Pipeline Orchestrator failed", error=str(e), exc_info=True)
            yield self._format_sse("ERROR", {"message": str(e)})
