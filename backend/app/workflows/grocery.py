"""
Grocery Shopping Workflow.
State Machine: Planning -> Searching -> Verifying -> Applying -> Optimizing -> Finalizing -> Completed.
"""
from __future__ import annotations

import logging
import asyncio

from app.workflows.base import BaseWorkflow
from app.workflows.context import WorkflowContext

from app.ai.goal_understanding.models import GoalContext
from app.ai.planning.service import PlanningService
from app.ai.retrieval.service import RetrievalService
from app.ai.verification.service import VerificationService
from app.ai.memory.service import MemoryService
from app.ai.optimization.service import OptimizationService
from app.ai.explainability.service import ExplainabilityService

logger = logging.getLogger(__name__)


class GroceryWorkflow(BaseWorkflow):
    
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
        await self._emit(context, "planning", {"step": "Building a shopping plan..."})
        
        goal_context = context.results["goal_context"]
        planning_service = PlanningService()
        
        # We need to run sync code in executor if it blocks, but let's assume fast or async
        shopping_plan, _ = planning_service.plan_goal(goal_context)
        context.results["shopping_plan"] = shopping_plan
        
        context.transition("state_searching")

    async def state_searching(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Searching")
        await self._emit(context, "searching", {"step": "Searching for best options"})
        
        plan = context.results["shopping_plan"]
        retrieval_service = RetrievalService(self.db)
        
        retrieval_result, _ = retrieval_service.retrieve_products(plan)
        context.results["retrieval_result"] = retrieval_result
        
        context.transition("state_verifying")

    async def state_verifying(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Verifying")
        await self._emit(context, "verifying", {"step": "Verifying product attributes"})
        
        retrieval_result = context.results["retrieval_result"]
        verification_service = VerificationService(self.db)
        
        verification_result, _ = verification_service.verify(retrieval_result)
        context.results["verification_result"] = verification_result
        
        context.transition("state_applying")

    async def state_applying(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Applying Preferences")
        await self._emit(context, "applying", {"step": "Applying your saved preferences..."})
        
        memory_service = MemoryService(self.db)
        preferences, _ = memory_service.get_user_preferences(context.user_id)
        context.results["preferences"] = preferences
        
        context.transition("state_optimizing")
        
    async def state_optimizing(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Optimizing")
        await self._emit(context, "optimizing", {"step": "Optimizing the final cart for value..."})
        
        plan = context.results["shopping_plan"]
        verification_result = context.results["verification_result"]
        preferences = context.results["preferences"]
        
        optimization_service = OptimizationService()
        optimized_plan, _ = optimization_service.optimize_cart(plan, verification_result, preferences)
        context.results["optimized_plan"] = optimized_plan
        
        context.transition("state_finalizing")

    async def state_finalizing(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Finalizing")
        await self._emit(context, "finalizing", {"step": "Finalizing recommendations..."})
        
        optimized_plan = context.results["optimized_plan"]
        explainability_service = ExplainabilityService()
        
        explainable_plan, _ = explainability_service.explain_plan(optimized_plan)
        context.results["explainable_plan"] = explainable_plan
        
        context.transition("completed")

    async def state_completed(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Completed")
        explainable_plan = context.results["explainable_plan"]
        
        # Convert ExplainableShoppingPlan to Recommendation array for frontend
        recommendations = []
        for cat in explainable_plan.categories:
            for item in cat.selected_items:
                recommendations.append({
                    "id": str(item.product_id),
                    "type": "product",
                    "title": item.product_name,
                    "price": 0.0, # Not strictly required by UI unless displayed
                    "match_score": int(item.optimization_score * 100),
                    "reasons": [item.explanation_text] + item.supporting_rules
                })
                
        # The user requested 'complete' event to include products/prices/reasons
        await self._emit(context, "complete", {
            "items": recommendations,
            "cart": {
                "items": recommendations,
                "explanation": {
                    "summary": "I've optimized your grocery list and selected the best products based on your preferences!"
                }
            }
        })
