from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.repositories.base import BaseRepository
from app.db.models.intelligence import TasteProfile, UserPreference

class IntelligenceRepository(BaseRepository[TasteProfile]):
    def __init__(self, db: Session):
        super().__init__(TasteProfile, db)
        
    def get_preference(self, user_id: int, category: str, key: str) -> Optional[UserPreference]:
        return self.db.query(UserPreference).filter_by(user_id=user_id, category=category, key=key).first()
        
    def get_all_preferences(self, user_id: int) -> List[UserPreference]:
        return self.db.query(UserPreference).filter_by(user_id=user_id).all()
        
    def save_preference(self, pref: UserPreference) -> UserPreference:
        self.db.add(pref)
        self.db.commit()
        self.db.refresh(pref)
        return pref
        
    def get_taste_profile(self, user_id: int) -> Optional[TasteProfile]:
        return self.db.query(TasteProfile).filter_by(user_id=user_id).first()
        
    def save_taste_profile(self, profile: TasteProfile) -> TasteProfile:
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
