from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.repositories.base import BaseRepository
from app.db.models.chat import ChatSession, ChatMessage

class MemoryRepository(BaseRepository[ChatSession]):
    def __init__(self, db: Session):
        super().__init__(ChatSession, db)
        
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        return self.db.query(ChatSession).filter_by(id=session_id).first()
        
    def get_session_by_user(self, session_id: str, user_id: int) -> Optional[ChatSession]:
        return self.db.query(ChatSession).filter_by(id=session_id, user_id=user_id).first()
        
    def get_messages(self, session_id: str, limit: int = 50) -> List[ChatMessage]:
        return self.db.query(ChatMessage)\
            .filter_by(session_id=session_id)\
            .order_by(ChatMessage.created_at.asc())\
            .limit(limit)\
            .all()
            
    def save_message(self, message: ChatMessage) -> ChatMessage:
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
        
    def save_session(self, session: ChatSession) -> ChatSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
