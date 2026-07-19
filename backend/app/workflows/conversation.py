"""
Conversation Manager.
Handles streaming inputs, manages the session state, and orchestrates intent + workflows.
"""
from __future__ import annotations

import logging
from sqlalchemy.orm import Session

from app.db.models.chat import ChatSession, ChatMessage, SessionStatus
from app.events.bus import event_bus, Event, EventType
from app.memory.session import SessionMemory
from app.workflows.intent import IntentResolver
from app.workflows.registry import WorkflowRegistry
from app.workflows.context import WorkflowContext
from app.db.repositories.memory import MemoryRepository

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, db: Session):
        self.repo = MemoryRepository(db)
        self.memory = SessionMemory(db)
        self.intent_resolver = IntentResolver()
        self.workflow_registry = WorkflowRegistry(db)
        # Note: self.db is no longer stored directly to enforce Repository pattern

    async def get_or_create_session(self, user_id: int, session_id: int | None = None) -> ChatSession:
        if session_id:
            session = self.repo.get_session_by_user(str(session_id), user_id)
            if session:
                return session

        session = ChatSession(user_id=user_id, status=SessionStatus.ACTIVE)
        session = self.repo.save_session(session)
        
        await event_bus.emit(Event(
            event_type=EventType.CONVERSATION_STARTED,
            user_id=user_id,
            session_id=str(session.id)
        ))
        
        return session

    async def process_message(self, user_id: int, session_id: int, content: str) -> dict:
        """
        Core orchestration loop:
        1. Save user message.
        2. Get history from SessionMemory.
        3. Resolve intent via LLM.
        4. Execute appropriate Workflow state machine.
        5. Return results to be sent back to user (SSE or REST).
        """
        # 1. Save Message
        user_msg = ChatMessage(session_id=str(session_id), role="user", content=content)
        self.repo.save_message(user_msg)

        # 2. Get recent context
        chat_history = self.memory.get_messages(str(session_id), limit=10)
        
        # 3. Resolve Intent
        intent_class = await self.intent_resolver.resolve(str(session_id), chat_history, content)
        
        if intent_class.needs_clarification:
            self._add_assistant_message(session_id, intent_class.clarification_question, intent=intent_class.intent_type)
            return {"type": "clarification", "message": intent_class.clarification_question}

        # 4. Execute Workflow
        context = WorkflowContext(
            session_id=str(session_id),
            user_id=user_id,
            intent=intent_class.domain or intent_class.intent_type,
            extracted_entities=intent_class.extracted_entities
        )
        
        completed_context = await self.workflow_registry.execute_workflow(context)
        
        # In a real app, use the results to generate a natural language response
        response_text = f"Executed {context.intent} workflow."
        
        # 5. Save assistant response
        self._add_assistant_message(session_id, response_text, intent=context.intent, structured_payload=str(completed_context.results))
        
        return {"type": "workflow_result", "message": response_text, "results": completed_context.results}

    def _add_assistant_message(self, session_id: int, content: str, intent: str | None = None, structured_payload: str | None = None) -> ChatMessage:
        msg = ChatMessage(
            session_id=str(session_id), 
            role="assistant", 
            content=content,
            intent=intent,
            structured_payload=structured_payload
        )
        msg = self.repo.save_message(msg)
        
        session = self.repo.get_session(str(session_id))
        if session:
            session.turn_count += 1
            self.repo.save_session(session)
            
        return msg
