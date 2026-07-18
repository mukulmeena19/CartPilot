from sqlalchemy.orm import Session
from app.db.models.user import User
from app.ai.memory.models import UserPreferenceContext
import json

class PreferenceStore:
    @staticmethod
    def get_preferences(db: Session, user_id: int) -> UserPreferenceContext:
        """
        Reads the JSONB preferences column and parses it into strict Pydantic models.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
            
        raw_prefs = user.preferences or {}
        return UserPreferenceContext(**raw_prefs)

    @staticmethod
    def save_preferences(db: Session, user_id: int, context: UserPreferenceContext) -> None:
        """
        Dumps the Pydantic model back to JSONB and commits to Postgres.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
            
        # dump with exclude_none to keep the json lean
        user.preferences = context.model_dump(exclude_none=True)
        db.commit()
