"""
Food Ordering Workflow.
State Machine: Restaurant Search -> Menu Analysis -> Ranking -> Recommend.
"""
from __future__ import annotations

import logging
from typing import Any

from app.workflows.base import BaseWorkflow

logger = logging.getLogger(__name__)


class FoodOrderingWorkflow(BaseWorkflow):
    
    async def execute(self, payload: dict) -> dict:
        await self.emit_started()
        
        try:
            # State 1: Restaurant Search (HybridRetriever)
            # State 2: Menu Analysis (LLM mapping user intent to menu items)
            # State 3: Ranking (PluginRanking)
            # State 4: Recommend
            
            logger.info(f"Executing Food Ordering Workflow for session {self.session_id}")
            result = {"status": "success", "domain": "food_ordering", "items": []}
            
            await self.emit_completed(result)
            return result
            
        except Exception as e:
            logger.error(f"Food Ordering workflow failed: {e}")
            await self.emit_failed(str(e))
            raise
