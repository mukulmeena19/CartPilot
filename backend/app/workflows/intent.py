"""
Intent Resolver.
Classifies the user's intent to route to the correct workflow.
"""
from __future__ import annotations

import logging
from typing import Any, Dict
from pydantic import BaseModel, Field

from app.providers.factory import get_llm_provider
from app.events.bus import event_bus, Event, EventType

logger = logging.getLogger(__name__)


class IntentClassification(BaseModel):
    intent_type: str = Field(
        description="Must be one of: new_request, follow_up, correction, cart_mod, preference_update, general_question"
    )
    confidence: float = Field(description="Confidence score from 0.0 to 1.0")
    domain: str | None = Field(description="If applicable, 'grocery' or 'food_ordering'")
    extracted_entities: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value pairs of extracted details (e.g. {'budget': 3000, 'cuisine': 'Italian'})"
    )
    needs_clarification: bool = Field(
        description="True if the request is too vague and we must ask a follow-up question."
    )
    clarification_question: str | None = Field(
        description="If needs_clarification is True, provide a natural conversational follow-up question."
    )


class IntentResolver:
    def __init__(self):
        self.llm = get_llm_provider()

    async def resolve(self, session_id: str, chat_history: str, latest_message: str) -> IntentClassification:
        """
        Uses the LLM Provider to parse intent.
        Strictly separated from business logic — returns a structured JSON model.
        """
        system_prompt = """
        You are the Intent Resolver for CartPilot, an AI Commerce Concierge.
        Your job is to analyze the user's latest message (given the history) and classify their intent.
        You do not execute searches or make recommendations. You just extract structured data.
        """
        
        result, _ = self.llm.generate_structured(
            system_prompt=system_prompt,
            user_prompt=f"History:\n{chat_history}\n\nLatest: {latest_message}",
            response_model=IntentClassification
        )
        
        await event_bus.emit(Event(
            event_type=EventType.INTENT_RESOLVED,
            session_id=session_id,
            payload={"intent_type": result.intent_type, "domain": result.domain}
        ))
        
        if result.needs_clarification:
            await event_bus.emit(Event(
                event_type=EventType.FOLLOW_UP_REQUIRED,
                session_id=session_id,
                payload={"question": result.clarification_question}
            ))
            
        return result
