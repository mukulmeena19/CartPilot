import time
import structlog
from typing import Tuple, Dict, Any
from app.ai.optimization.models import OptimizedShoppingPlan
from app.ai.explainability.models import ExplainableShoppingPlan, ExplainableCategory
from app.ai.explainability.explanation_builder import ExplanationBuilder

logger = structlog.get_logger(__name__)

class ExplainabilityService:
    def explain_plan(self, plan: OptimizedShoppingPlan) -> Tuple[ExplainableShoppingPlan, Dict[str, Any]]:
        start_time = time.time()
        logger.info("Starting explainability engine")
        
        try:
            explainable_categories = []
            
            for cat in plan.categories:
                explained_items = []
                for cand in cat.selected_items:
                    explanation = ExplanationBuilder.build_explanation(cand)
                    explained_items.append(explanation)
                    
                explainable_categories.append(
                    ExplainableCategory(
                        category_name=cat.allocation.name,
                        selected_items=explained_items,
                        total_cost=cat.total_cost
                    )
                )
                
            result = ExplainableShoppingPlan(
                categories=explainable_categories,
                total_budget_used=plan.total_budget_used,
                total_budget_allocated=plan.total_budget_allocated,
                optimization_success_rate=plan.optimization_success_rate
            )
            
            latency = time.time() - start_time
            logger.info("Explainability generation complete", latency_sec=latency)
            
            return result, {"latency_sec": latency}
            
        except Exception as e:
            logger.error("Explainability engine failed", error=str(e))
            raise
