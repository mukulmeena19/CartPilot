"""
Session Memory Manager.
Maintains the active context window for the LLM and compresses history.
"""
from __future__ import annotations

import logging
from typing import List, Dict
from sqlalchemy.orm import Session

from app.db.models.chat import ChatSession, ChatMessage
from app.providers.factory import get_llm_provider

logger = logging.getLogger(__name__)


class SessionMemory:
    def __init__(self, db: Session):
        self.db = db
        self.llm = get_llm_provider()

    def get_recent_history(self, session_id: int, limit: int = 10) -> str:
        """
        Retrieves the N most recent messages to form the immediate context window.
        """
        messages = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all()
        )
        
        # Reverse to chronological order
        messages.reverse()
        
        history_str = ""
        for msg in messages:
            history_str += f"{msg.role.upper()}: {msg.content}\n"
            
        return history_str.strip()

    async def compress_history(self, session_id: int) -> None:
        """
        Periodically compresses older messages into a summary to avoid LLM context limits.
        Called asynchronously by the Workflow Engine when turn_count hits a threshold.
        """
        session = self.db.query(ChatSession).filter_by(id=session_id).first()
        if not session or session.turn_count < 20:
            return

        # Simple threshold check for compression
        # Full implementation would use the LLM to generate a summary of older messages
        # and update session.conversation_summary
        pass
