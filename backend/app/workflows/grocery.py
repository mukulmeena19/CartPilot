"""
Grocery Shopping Workflow.
State Machine: Recipe Understanding -> Ingredient Expansion -> Hybrid Search -> Cart.
"""
from __future__ import annotations

import logging

from app.workflows.base import BaseWorkflow
from app.workflows.context import WorkflowContext

logger = logging.getLogger(__name__)


class GroceryWorkflow(BaseWorkflow):
    
    def register_states(self) -> None:
        self.states = {
            "init": self.state_init,
            "recipe_understanding": self.state_recipe_understanding,
            "ingredient_expansion": self.state_ingredient_expansion,
            "hybrid_search": self.state_hybrid_search,
            "completed": self.state_completed
        }

    async def state_init(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Initialization")
        context.transition("recipe_understanding")
        
    async def state_recipe_understanding(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Recipe Understanding")
        # In a real impl, parse recipes from LLM entities
        context.transition("ingredient_expansion")

    async def state_ingredient_expansion(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Ingredient Expansion")
        # Use KnowledgeService to expand ingredients to substitutes
        context.transition("hybrid_search")

    async def state_hybrid_search(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Hybrid Search")
        # Use HybridRetriever to fetch products
        context.results["products"] = []
        context.transition("completed")

    async def state_completed(self, context: WorkflowContext) -> None:
        pass
