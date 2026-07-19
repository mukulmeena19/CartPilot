"""
Trend Engine.
Exposes APIs for the Plugin Ranking system to factor in platform popularity and seasonality.
"""
from __future__ import annotations

import logging
from typing import Dict
from sqlalchemy.orm import Session

from app.db.models.analytics import TrendSnapshot, MarketBasketAssociation

logger = logging.getLogger(__name__)


class TrendEngine:
    def __init__(self, db: Session):
        self.db = db

    def get_trending_boosts(self, entity_type: str) -> Dict[int, float]:
        """
        Returns a dictionary mapping entity_id to a trend boost score (0.0 to 1.0).
        Used by the Ranking Engine to boost currently popular items.
        """
        # In a real implementation, this would cache the latest TrendSnapshot table.
        # For Phase 6 scaffolding, we query the DB directly.
        trends = (
            self.db.query(TrendSnapshot)
            .filter(TrendSnapshot.entity_type == entity_type)
            .filter(TrendSnapshot.timeframe == "weekly")
            .all()
        )
        
        return {t.entity_id: t.score for t in trends}

    def get_market_basket_boosts(self, cart_item_ids: list[int]) -> Dict[int, float]:
        """
        Given a list of items already in the user's cart, returns related items 
        and their association strength (confidence * lift).
        Used to boost "Frequently Bought Together" items in the search results.
        """
        if not cart_item_ids:
            return {}
            
        associations = (
            self.db.query(MarketBasketAssociation)
            .filter(MarketBasketAssociation.item_a_id.in_(cart_item_ids))
            # Filter for strong rules only
            .filter(MarketBasketAssociation.lift > 1.2)
            .filter(MarketBasketAssociation.confidence > 0.3)
            .all()
        )
        
        boosts: Dict[int, float] = {}
        for assoc in associations:
            # Simple boost calculation based on rule strength
            score = min(1.0, assoc.confidence * (assoc.lift / 10.0))
            
            # If multiple cart items suggest the same product, take the max boost
            if assoc.item_b_id in boosts:
                boosts[assoc.item_b_id] = max(boosts[assoc.item_b_id], score)
            else:
                boosts[assoc.item_b_id] = score
                
        return boosts
