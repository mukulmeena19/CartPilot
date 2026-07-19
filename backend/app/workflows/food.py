"""
Food Ordering Workflow.
State Machine: Restaurant Search -> Menu Analysis -> Ranking -> Recommend.
"""
from __future__ import annotations

import logging

from app.workflows.base import BaseWorkflow
from app.workflows.context import WorkflowContext

logger = logging.getLogger(__name__)


class FoodOrderingWorkflow(BaseWorkflow):
    
    def register_states(self) -> None:
        self.states = {
            "init": self.state_init,
            "restaurant_search": self.state_restaurant_search,
            "menu_analysis": self.state_menu_analysis,
            "ranking": self.state_ranking,
            "completed": self.state_completed
        }

    async def state_init(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Initialization")
        context.transition("restaurant_search")
        
    async def state_restaurant_search(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Restaurant Search")
        # Use HybridRetriever for restaurants
        context.transition("menu_analysis")

    async def state_menu_analysis(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Menu Analysis")
        # LLM analyzes menus to match intent
        context.transition("ranking")

    async def state_ranking(self, context: WorkflowContext) -> None:
        logger.info(f"[{self.__class__.__name__}] Ranking")
        # PluginRanker scores the items
        context.results["menu_items"] = []
        context.transition("completed")

    async def state_completed(self, context: WorkflowContext) -> None:
        pass
