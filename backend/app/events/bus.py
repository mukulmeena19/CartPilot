"""
Event Bus — lightweight pub/sub system.
Services emit events; subscribers react independently.
This decouples modules and improves observability.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Awaitable, Dict, List
import uuid

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    # Conversation
    CONVERSATION_STARTED = "conversation.started"
    FOLLOW_UP_REQUIRED = "conversation.follow_up_required"
    INTENT_RESOLVED = "conversation.intent_resolved"

    # Workflow
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"

    # Commerce Engine
    RETRIEVAL_COMPLETED = "engine.retrieval_completed"
    RANKING_COMPLETED = "engine.ranking_completed"
    OPTIMIZATION_COMPLETED = "engine.optimization_completed"
    RECOMMENDATION_GENERATED = "engine.recommendation_generated"

    # Cart
    CART_UPDATED = "cart.updated"

    # Streaming
    STREAMING_STARTED = "streaming.started"
    STREAMING_COMPLETED = "streaming.completed"

    # Analytics
    RECOMMENDATION_SHOWN = "analytics.recommendation_shown"
    RECOMMENDATION_CLICKED = "analytics.recommendation_clicked"
    RECOMMENDATION_IGNORED = "analytics.recommendation_ignored"
    RECOMMENDATION_PURCHASED = "analytics.recommendation_purchased"
    RECOMMENDATION_FEEDBACK = "analytics.recommendation_feedback"


@dataclass
class Event:
    event_type: EventType
    payload: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: int | None = None
    session_id: str | None = None


# Type alias for async event handlers
AsyncHandler = Callable[[Event], Awaitable[None]]


class EventBus:
    """
    In-process async event bus.
    Designed to be replaced with Redis Pub/Sub or a message broker in production.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[EventType, List[AsyncHandler]] = {}

    def subscribe(self, event_type: EventType, handler: AsyncHandler) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    async def emit(self, event: Event) -> None:
        handlers = self._subscribers.get(event.event_type, [])
        if not handlers:
            return
        results = await asyncio.gather(
            *[handler(event) for handler in handlers],
            return_exceptions=True,
        )
        for result in results:
            if isinstance(result, Exception):
                logger.error(
                    "Event handler raised an exception",
                    exc_info=result,
                    extra={"event_type": event.event_type, "event_id": event.event_id},
                )


# Global singleton — import this across the app
event_bus = EventBus()
