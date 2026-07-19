"""
Learning & Analytics DB Models.
Stores platform-wide, anonymous, aggregated intelligence.
Never store individual user identities here.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base


class AnalyticsEvent(Base):
    """
    Raw, anonymous event stream used for aggregation.
    """
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    
    # An anonymous session ID (not tied to Users table)
    anonymous_session_id = Column(String, index=True, nullable=False)
    
    event_type = Column(String, index=True, nullable=False) # e.g. "recommendation_impression", "purchase"
    payload = Column(JSON, nullable=False)                  # Contains entity IDs, timestamps, search terms
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class TrendSnapshot(Base):
    """
    Aggregated popularity scores for items over time.
    Generated via cron jobs.
    """
    __tablename__ = "trend_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    
    entity_type = Column(String, index=True, nullable=False) # "product", "restaurant", "recipe"
    entity_id = Column(Integer, index=True, nullable=False)
    
    # "daily", "weekly", "seasonal"
    timeframe = Column(String, index=True, nullable=False)
    
    score = Column(Float, nullable=False)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())


class MarketBasketAssociation(Base):
    """
    Learned association rules ("People who bought X also bought Y").
    Used to boost rankings when X is already in the cart.
    """
    __tablename__ = "market_basket_associations"

    id = Column(Integer, primary_key=True, index=True)
    
    item_a_id = Column(Integer, index=True, nullable=False)
    item_b_id = Column(Integer, index=True, nullable=False)
    
    support = Column(Float, nullable=False)    # How often A and B appear together overall
    confidence = Column(Float, nullable=False) # Probability of buying B given A
    lift = Column(Float, nullable=False)       # Strength of association (Lift > 1 implies strong rule)
    
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
