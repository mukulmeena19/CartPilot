"""
Workflow Registry.
Routes intents to specific workflow state machines.
"""
from __future__ import annotations

import logging
from typing import Dict, Type
from sqlalchemy.orm import Session

from app.workflows.base import BaseWorkflow
from app.workflows.grocery import GroceryWorkflow
from app.workflows.food import FoodOrderingWorkflow
from app.workflows.context import WorkflowContext

logger = logging.getLogger(__name__)


class WorkflowRegistry:
    def __init__(self, db: Session):
        self.db = db
        self.registry: Dict[str, Type[BaseWorkflow]] = {
            "grocery": GroceryWorkflow,
            "food_ordering": FoodOrderingWorkflow
        }

    async def execute_workflow(self, context: WorkflowContext) -> WorkflowContext:
        """Instantiates the correct workflow based on intent domain and executes it."""
        domain = context.intent
        
        workflow_cls = self.registry.get(domain)
        if not workflow_cls:
            logger.error(f"No workflow registered for domain: {domain}")
            context.transition("failed")
            context.errors.append(f"No workflow for {domain}")
            return context
            
        workflow = workflow_cls()
        # In a real app, you might pass dependencies via DI here instead of tightly coupling
        return await workflow.execute(context)
