import time
import structlog
from typing import Tuple, Dict, Any, Optional
from app.ai.planning.models import ShoppingPlan
from app.ai.verification.models import VerificationResult
from app.ai.memory.models import UserPreferenceContext
from app.ai.optimization.models import OptimizedShoppingPlan
from app.ai.optimization.optimizer import ShoppingOptimizer

logger = structlog.get_logger(__name__)

class OptimizationService:
    def __init__(self):
        self.optimizer = ShoppingOptimizer()

    def optimize_cart(
        self,
        plan: ShoppingPlan,
        verification_result: VerificationResult,
        preferences: Optional[UserPreferenceContext]
    ) -> Tuple[OptimizedShoppingPlan, Dict[str, Any]]:
        start_time = time.time()
        logger.info("Starting shopping optimization engine")
        
        try:
            result = self.optimizer.optimize(plan, verification_result, preferences)
            
            latency = time.time() - start_time
            logger.info(
                "Optimization complete",
                latency_sec=latency,
                success_rate=result.optimization_success_rate,
                budget_used=result.total_budget_used
            )
            
            return result, {"latency_sec": latency}
            
        except Exception as e:
            logger.error("Optimization engine failed", error=str(e))
            raise
