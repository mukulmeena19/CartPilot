"""
Food Ordering Workflow.
State Machine: Planning -> Searching -> Verifying -> Applying -> Optimizing -> Finalizing -> Completed.
"""
from __future__ import annotations

import logging
import asyncio

from app.workflows.base import BaseWorkflow
from app.workflows.context import WorkflowContext
from app.ai.goal_understanding.models import GoalContext

logger = logging.getLogger(__name__)


class FoodOrderingWorkflow(BaseWorkflow):
    
    def register_states(self) -> None:
        self.states = {
            "init": self.state_init,
            "state_planning": self.state_planning,
            "state_searching": self.state_searching,
            "state_verifying": self.state_verifying,
            "state_applying": self.state_applying,
            "state_optimizing": self.state_optimizing,
            "state_finalizing": self.state_finalizing,
            "completed": self.state_completed
        }

    async def _emit(self, context: WorkflowContext, event_type: str, data: dict = None):
        if context.emit_cb:
            await context.emit_cb(event_type, data or {})

    async def state_init(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Initialization")
        context.results["goal_context"] = GoalContext(**context.extracted_entities)
        context.transition("state_planning")
        
    async def state_planning(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Planning")
        await self._emit(context, "planning", {"step": "Planning your food order..."})
        
        goal_context = context.results["goal_context"]
        from app.ai.planning.service import PlanningService
        planning_service = PlanningService()
        
        shopping_plan, _ = planning_service.plan_goal(goal_context)
        context.results["shopping_plan"] = shopping_plan
        
        context.transition("state_searching")

    async def state_searching(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Searching")
        await self._emit(context, "searching", {"step": "Searching for nearby restaurants..."})
        
        plan = context.results["shopping_plan"]
        from app.ai.retrieval.service import RetrievalService
        retrieval_service = RetrievalService(self.db)
        
        retrieval_result, _ = retrieval_service.retrieve_products(plan, domain="food", goal_context=context.results["goal_context"])
        context.results["retrieval_result"] = retrieval_result
        
        context.transition("state_verifying")

    async def state_verifying(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Verifying")
        await self._emit(context, "verifying", {"step": "Verifying menu items..."})
        
        retrieval_result = context.results["retrieval_result"]
        from app.ai.verification.service import VerificationService
        verification_service = VerificationService(self.db)
        
        verification_result, _ = verification_service.verify(retrieval_result)
        context.results["verification_result"] = verification_result
        
        context.transition("state_applying")

    async def state_applying(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Applying")
        await self._emit(context, "applying", {"step": "Applying your preferences..."})
        
        from app.ai.memory.service import MemoryService
        memory_service = MemoryService(self.db)
        preferences, _ = memory_service.get_user_preferences(context.user_id)
        context.results["preferences"] = preferences
        
        context.transition("state_optimizing")

    async def state_optimizing(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Optimizing")
        await self._emit(context, "optimizing", {"step": "Optimizing order..."})
        
        plan = context.results["shopping_plan"]
        verification_result = context.results["verification_result"]
        preferences = context.results["preferences"]
        
        from app.ai.optimization.service import OptimizationService
        optimization_service = OptimizationService()
        optimized_plan, _ = optimization_service.optimize_cart(plan, verification_result, preferences)
        context.results["optimized_plan"] = optimized_plan
        
        context.transition("state_finalizing")

    async def state_finalizing(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Finalizing")
        await self._emit(context, "finalizing", {"step": "Finalizing recommendations..."})
        
        optimized_plan = context.results["optimized_plan"]
        from app.ai.explainability.service import ExplainabilityService
        explainability_service = ExplainabilityService()
        
        explainable_plan, _ = explainability_service.explain_plan(optimized_plan)
        context.results["explainable_plan"] = explainable_plan
        
        context.transition("completed")

    async def state_completed(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Completed")
        explainable_plan = context.results["explainable_plan"]
        
        recommendations = []
        for cat in explainable_plan.categories:
            for item in cat.selected_items:
                recommendations.append({
                    "id": str(item.product_id),
                    "type": "restaurant",  # use restaurant type for UI
                    "title": item.product_name,
                    "price": 0.0,
                    "estimated_price": item.optimization_score * 10, # mock price for ui if needed
                    "rating": 4.5,
                    "delivery_time_mins": 30,
                    "match_score": int(item.optimization_score * 100),
                    "reasons": [item.explanation_text] + item.supporting_rules
                })
        
        if not recommendations:
            fallback_message = "I couldn't find any restaurant options matching your request right now."
            await self._emit(context, "complete", {
                "items": [],
                "cart": {
                    "items": [],
                    "explanation": {
                        "summary": fallback_message
                    }
                }
            })
            return

        await self._emit(context, "complete", {
            "items": recommendations,
            "cart": {
                "items": recommendations,
                "explanation": {
                    "summary": explainable_plan.summary or "I found the best restaurant options for you!"
                }
            }
        })
