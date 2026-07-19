"""
Conversation Manager.
Handles streaming inputs, manages the session state, and emits events.
"""
from __future__ import annotations

import logging
from sqlalchemy.orm import Session

from app.db.models.chat import ChatSession, ChatMessage, SessionStatus
from app.events.bus import event_bus, Event, EventType

logger = logging.getLogger(__name__)


class ConversationManager:
    def __init__(self, db: Session):
        self.db = db

    async def get_or_create_session(self, user_id: int, session_id: int | None = None) -> ChatSession:
        if session_id:
            session = self.db.query(ChatSession).filter_by(id=session_id, user_id=user_id).first()
            if session:
                return session

        session = ChatSession(user_id=user_id, status=SessionStatus.ACTIVE)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        await event_bus.emit(Event(
            event_type=EventType.CONVERSATION_STARTED,
            user_id=user_id,
            session_id=str(session.id)
        ))
        
        return session

    def add_user_message(self, session_id: int, content: str) -> ChatMessage:
        msg = ChatMessage(session_id=session_id, role="user", content=content)
        self.db.add(msg)
        
        session = self.db.query(ChatSession).filter_by(id=session_id).first()
        if session:
            session.turn_count += 1
            
        self.db.commit()
        self.db.refresh(msg)
        return msg
        
    def add_assistant_message(self, session_id: int, content: str, intent: str = None, structured_payload: str = None) -> ChatMessage:
        msg = ChatMessage(
            session_id=session_id, 
            role="assistant", 
            content=content,
            intent=intent,
            structured_payload=structured_payload
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg
