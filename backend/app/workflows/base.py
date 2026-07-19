"""
Base Workflow Engine.
State machine orchestrator for commerce domains.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Dict, Callable, Awaitable

from app.workflows.context import WorkflowContext
from app.events.bus import event_bus, Event, EventType

logger = logging.getLogger(__name__)


class BaseWorkflow(ABC):
    """
    Abstract State Machine.
    """
    def __init__(self):
        self.states: Dict[str, Callable[[WorkflowContext], Awaitable[None]]] = {}
        self.register_states()

    @abstractmethod
    def register_states(self) -> None:
        """Register state transition methods."""
        pass

    async def execute(self, context: WorkflowContext) -> WorkflowContext:
        """
        Executes the workflow state machine until 'completed' or 'failed'.
        """
        await self.emit_started(context)
        
        try:
            while context.current_state not in ["completed", "failed"]:
                handler = self.states.get(context.current_state)
                if not handler:
                    raise ValueError(f"Invalid state: {context.current_state}")
                
                logger.info(f"[{self.__class__.__name__}] Executing state: {context.current_state}")
                await handler(context)
                
            if context.current_state == "completed":
                await self.emit_completed(context)
            else:
                await self.emit_failed(context, "Failed during execution")
                
        except Exception as e:
            logger.exception(f"Workflow {self.__class__.__name__} failed")
            context.transition("failed")
            context.errors.append(str(e))
            await self.emit_failed(context, str(e))
            
        return context

    async def emit_started(self, context: WorkflowContext) -> None:
        await event_bus.emit(Event(
            event_type=EventType.WORKFLOW_STARTED,
            session_id=context.session_id,
            payload={"workflow": self.__class__.__name__, "intent": context.intent}
        ))

    async def emit_completed(self, context: WorkflowContext) -> None:
        await event_bus.emit(Event(
            event_type=EventType.WORKFLOW_COMPLETED,
            session_id=context.session_id,
            payload={"workflow": self.__class__.__name__, "results": context.results}
        ))

    async def emit_failed(self, context: WorkflowContext, error: str) -> None:
        await event_bus.emit(Event(
            event_type=EventType.WORKFLOW_FAILED,
            session_id=context.session_id,
            payload={"workflow": self.__class__.__name__, "error": error}
        ))
