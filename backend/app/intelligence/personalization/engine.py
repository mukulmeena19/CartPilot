"""
Personalization Engine.
Adjusts scores, generates search filters, and manages user taste profiles.
"""
from __future__ import annotations

import structlog
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.repositories.intelligence import IntelligenceRepository
from app.db.models.intelligence import TasteProfile, UserPreference
from app.ai.retrieval.models import ProductCandidate

logger = structlog.get_logger(__name__)

class PersonalizationEngine:
    def __init__(self, db: Session):
        self.repo = IntelligenceRepository(db)
        self.db = db

    def cold_start_profile(self, user_id: int, initial_preferences: Dict[str, Any]) -> TasteProfile:
        """Initialize a new TasteProfile for a user based on onboarding data."""
        try:
            profile = TasteProfile(
                user_id=user_id,
                cuisine_affinities=initial_preferences.get("cuisines", {}),
                brand_affinities=initial_preferences.get("brands", {})
            )
            self.repo.save_taste_profile(profile)
            
            # Also create explicit UserPreferences
            for cuisine, score in initial_preferences.get("cuisines", {}).items():
                self.update_preferences(user_id, "cuisine", cuisine, score, "explicit")
                
            for brand, score in initial_preferences.get("brands", {}).items():
                self.update_preferences(user_id, "brand", brand, score, "explicit")

            logger.info("Cold start profile created", user_id=user_id)
            return profile
        except Exception as e:
            logger.error("Failed to create cold start profile", error=str(e), user_id=user_id)
            # Raise so tests can catch it
            raise

    def update_preferences(self, user_id: int, category: str, key: str, affinity: float, source: str = "explicit") -> UserPreference:
        """
        Incrementally updates a specific user preference score.
        """
        try:
            pref = self.repo.get_preference(user_id, category, key)
            if pref:
                pref.affinity = min(1.0, max(-1.0, pref.affinity + affinity))
                self.repo.save_preference(pref)
            else:
                new_pref = UserPreference(
                    user_id=user_id,
                    category=category,
                    key=key,
                    affinity=affinity,
                    source=source
                )
                self.repo.save_preference(new_pref)
                pref = new_pref
            return pref
        except Exception as e:
            logger.error("Failed to update preference", error=str(e), user_id=user_id, category=category, key=key)
            raise

    def calculate_affinity(self, user_id: int, candidates: List[ProductCandidate]) -> List[ProductCandidate]:
        """
        Adjusts product candidate scores based on explicit user preferences.
        """
        try:
            prefs = self.repo.get_all_preferences(user_id)
            if not prefs:
                return candidates

            brand_prefs = {p.key: p.affinity for p in prefs if p.category == 'brand'}
            
            for candidate in candidates:
                if candidate.brand and candidate.brand in brand_prefs:
                    affinity = brand_prefs[candidate.brand]
                    if affinity > 0:
                        bump = affinity * 0.05
                        candidate.similarity_score = min(1.0, candidate.similarity_score + bump)
                        candidate.reasoning = candidate.reasoning or ""
                        candidate.reasoning += f" [Matches favorite brand: {candidate.brand}]"

            candidates.sort(key=lambda x: x.similarity_score, reverse=True)
            return candidates
        except Exception as e:
            logger.error("Failed to calculate affinity", error=str(e), user_id=user_id)
            return candidates

    def generate_filters(self, user_id: int) -> Dict[str, Any]:
        filters = {}
        try:
            prefs = self.repo.get_all_preferences(user_id)
            allergies = [p.key for p in prefs if p.category == 'allergy' and p.affinity < 0]
            if allergies:
                filters["exclude_ingredients"] = allergies
        except Exception as e:
            logger.error("Failed to generate filters", error=str(e), user_id=user_id)
        
        return filters
