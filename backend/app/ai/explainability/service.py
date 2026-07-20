import time
import json
import structlog
from typing import Tuple, Dict, Any
from app.ai.optimization.models import OptimizedShoppingPlan
from app.ai.explainability.models import ExplainableShoppingPlan, ExplainableCategory
from app.ai.explainability.explanation_builder import ExplanationBuilder
from app.ai.providers import get_llm_provider

logger = structlog.get_logger(__name__)

class ExplainabilityService:
    def __init__(self):
        self.provider = get_llm_provider()

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
            
            # Generate LLM summary
            try:
                items_context = []
                for cat in explainable_categories:
                    for item in cat.selected_items:
                        items_context.append(f"- {item.product_name} (₹{item.optimization_score*10:.2f}): {item.explanation_text}")
                        
                prompt = (
                    "You are a helpful AI shopping assistant. Write a short, natural language summary (1-2 sentences) "
                    "about the following cart items you selected for the user. Do not invent any discounts, prices, or products "
                    "that are not listed below. Do not use markdown.\n\n"
                    f"Selected Items:\n{chr(10).join(items_context)}"
                )
                
                # Using a generic fast model call (we don't need JSON here)
                llm_response = self.provider.generate(
                    prompt=prompt,
                    system_prompt="You are a concise shopping assistant.",
                    temperature=0.3,
                )
                
                # Check if generate returns string or object.
                if isinstance(llm_response, dict) and "text" in llm_response:
                    result.summary = llm_response["text"].strip()
                elif hasattr(llm_response, "text"):
                    result.summary = llm_response.text.strip()
                else:
                    result.summary = str(llm_response).strip()
                    
            except Exception as llm_e:
                logger.warning("Failed to generate explainability summary", error=str(llm_e))
                result.summary = "I've optimized your list and selected the best products based on your preferences!"
            
            latency = time.time() - start_time
            logger.info("Explainability generation complete", latency_sec=latency)
            
            return result, {"latency_sec": latency}
            
        except Exception as e:
            logger.error("Explainability engine failed", error=str(e))
            raise
