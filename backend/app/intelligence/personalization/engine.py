"""
Personalization Engine.
Generates deterministic affinity scores and retrieval filters for a user.
"""
from __future__ import annotations

import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.db.models.intelligence import TasteProfile, UserPreference

logger = logging.getLogger(__name__)


class PersonalizationEngine:
    def __init__(self, db: Session):
        self.db = db

    def get_user_taste_profile(self, user_id: int) -> TasteProfile | None:
        """Fetch the pre-computed TasteProfile."""
        return self.db.query(TasteProfile).filter(TasteProfile.user_id == user_id).first()

    def get_active_preferences(self, user_id: int) -> List[UserPreference]:
        """Fetch explicit and strongly implicit preferences."""
        return (
            self.db.query(UserPreference)
            .filter(UserPreference.user_id == user_id)
            .filter(UserPreference.affinity > 0.0)
            .all()
        )

    def generate_retrieval_filters(self, user_id: int) -> Dict[str, Any]:
        """
        Generate hard filters for semantic search (e.g. MUST NOT contain allergens, MUST be Vegan).
        These bypass LLM reasoning and guarantee safety/compliance with explicit user settings.
        """
        prefs = self.get_active_preferences(user_id)
        
        filters = {
            "must_not": [],
            "must": []
        }
        
        for pref in prefs:
            if pref.category == "allergy" and pref.affinity < 0.1:
                filters["must_not"].append(pref.key)
            elif pref.category == "dietary" and pref.affinity > 0.9:
                filters["must"].append(pref.key)
                
        return filters

    def get_affinity_boosts(self, user_id: int) -> Dict[str, Dict[str, float]]:
        """
        Returns dictionaries of affinities to be injected into the Plugin Ranking Engine.
        Returns:
            {"cuisine": {"Indian": 0.8, "Italian": 0.4}, "brand": {"Amul": 0.9}}
        """
        profile = self.get_user_taste_profile(user_id)
        if not profile:
            return {"cuisine": {}, "brand": {}}
            
        return {
            "cuisine": profile.cuisine_affinities or {},
            "brand": profile.brand_affinities or {}
        }
