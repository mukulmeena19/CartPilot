from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.repositories.memory import MemoryRepository
from app.db.models.chat import ChatSession, ChatMessage

class SessionMemory:
    def __init__(self, db: Session):
        self.repo = MemoryRepository(db)

    def get_messages(self, session_id: str, limit: int = 50) -> List[ChatMessage]:
        return self.repo.get_messages(session_id, limit)
        
    def add_message(self, session_id: str, sender: str, content: str, payload: dict = None) -> ChatMessage:
        msg = ChatMessage(
            session_id=session_id,
            sender=sender,
            content=content,
            payload=payload or {}
        )
        return self.repo.save_message(msg)
        
    def create_session(self, session_id: str, user_id: int) -> ChatSession:
        session = ChatSession(id=session_id, user_id=user_id)
        return self.repo.save_session(session)
        
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        return self.repo.get_session(session_id)
