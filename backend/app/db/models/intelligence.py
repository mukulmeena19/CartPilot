"""
User Intelligence DB Models.
Stores both explicit preferences and implicit behavioral history.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.config import settings
from app.db.base import Base


class TasteProfile(Base):
    """
    Aggregate semantic representation of a user's taste.
    Updated periodically based on history and preferences.
    """
    __tablename__ = "taste_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    # The semantic embedding representing their combined tastes
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=True)
    
    # Pre-computed affinity maps for fast ranking (e.g. {"Indian": 0.9, "Chinese": 0.4})
    cuisine_affinities = Column(JSON, default=dict)
    brand_affinities = Column(JSON, default=dict)
    
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="taste_profile")


class UserPreference(Base):
    """
    Explicit or strongly-inferred user preferences.
    """
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    category = Column(String, nullable=False, index=True) # "dietary", "allergy", "cuisine", "brand"
    key = Column(String, nullable=False)                  # e.g., "Vegan", "Peanuts", "Indian", "Amul"
    value = Column(String, nullable=True)                 # For scalar preferences, e.g., "budget_limit" -> "3000"
    
    # 0.0 (hate) to 1.0 (love)
    affinity = Column(Float, default=1.0)
    
    # "explicit" (user told us) or "implicit" (learned from behavior)
    source = Column(String, default="implicit")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="preferences")


class BehavioralHistory(Base):
    """
    Raw stream of user interactions used to train the TasteProfile.
    """
    __tablename__ = "behavioral_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    action_type = Column(String, nullable=False, index=True) # "search", "view", "cart_add", "purchase"
    entity_type = Column(String, nullable=False)             # "product", "restaurant", "recipe"
    entity_id = Column(Integer, nullable=False)
    
    context = Column(JSON, nullable=True)                    # e.g. search query that led to this
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="behavioral_history")


class RecommendationFeedback(Base):
    """
    Explicit feedback on AI recommendations.
    """
    __tablename__ = "recommendation_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    recommendation_id = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    
    # 1: Helpful, -1: Not Interested, -2: Never Recommend
    feedback_score = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="recommendation_feedback")
