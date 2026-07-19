"""
Base Workflow Engine.
State machine orchestrator for commerce domains.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

from app.events.bus import event_bus, Event, EventType

logger = logging.getLogger(__name__)


class BaseWorkflow(ABC):
    def __init__(self, db: Session, session_id: str):
        self.db = db
        self.session_id = session_id

    @abstractmethod
    async def execute(self, payload: dict) -> dict:
        """
        Executes the workflow state machine.
        Must be implemented by subclasses.
        """
        pass

    async def emit_started(self) -> None:
        await event_bus.emit(Event(
            event_type=EventType.WORKFLOW_STARTED,
            session_id=self.session_id,
            payload={"workflow": self.__class__.__name__}
        ))

    async def emit_completed(self, result: dict) -> None:
        await event_bus.emit(Event(
            event_type=EventType.WORKFLOW_COMPLETED,
            session_id=self.session_id,
            payload={"workflow": self.__class__.__name__, "result": result}
        ))

    async def emit_failed(self, error: str) -> None:
        await event_bus.emit(Event(
            event_type=EventType.WORKFLOW_FAILED,
            session_id=self.session_id,
            payload={"workflow": self.__class__.__name__, "error": error}
        ))
