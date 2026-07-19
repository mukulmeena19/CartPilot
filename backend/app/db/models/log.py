from sqlalchemy import Column, String, Float, JSON, Integer, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True) # Optional, null if anonymous
    query = Column(String, index=True, nullable=False)
    candidate_id = Column(String, index=True, nullable=False)
    
    # Score details
    semantic_score = Column(Float, nullable=False)
    fts_score = Column(Float, nullable=False)
    plugin_scores = Column(JSON, nullable=False) # Store the JSON payload of all plugin scores
    final_score = Column(Float, nullable=False)
    reasons = Column(JSON, nullable=False) # JSON array of reasons
    
    latency_ms = Column(Float, nullable=False) # Total pipeline latency to generate this candidate's recommendation
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
