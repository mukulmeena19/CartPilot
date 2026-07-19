from typing import List, Dict, Any
from sqlalchemy.orm import Session
import structlog
from app.db.repositories.analytics import AnalyticsRepository
from app.db.models.analytics import AnalyticsEvent

logger = structlog.get_logger(__name__)

class TrendEngine:
    def __init__(self, db: Session):
        self.repo = AnalyticsRepository(db)
        self.db = db

    def record_event(self, anonymous_session_id: str, event_type: str, payload: Dict[str, Any]) -> None:
        """Record an anonymous event for later aggregation."""
        event = AnalyticsEvent(
            anonymous_session_id=anonymous_session_id,
            event_type=event_type,
            payload=payload
        )
        self.db.add(event)
        self.db.commit()

    def aggregate_daily(self) -> None:
        pass

    def get_trending_products(self, limit: int = 10) -> List[int]:
        """
        Returns a list of trending product IDs based on recent aggregated snapshot scores.
        """
        try:
            results = self.repo.get_top_trending_products(limit)
            return [product_id for product_id, _ in results]
        except Exception as e:
            logger.error("Failed to fetch trending products", error=str(e))
            return []

    def get_trending_restaurants(self, limit: int = 10) -> List[int]:
        # Simple stub for now
        return []

    def get_popular_cuisines(self, limit: int = 5) -> List[str]:
        """
        Returns a list of popular cuisines.
        """
        try:
            results = self.repo.get_top_trending_cuisines(limit)
            return [cuisine for cuisine, _ in results]
        except Exception as e:
            logger.error("Failed to fetch popular cuisines", error=str(e))
            return []

    def get_market_basket(self, item_ids: List[int], limit: int = 5, min_lift: float = 1.2, min_confidence: float = 0.3) -> Dict[int, float]:
        """
        Returns frequently bought together items based on association rules.
        """
        if not item_ids:
            return {}
            
        try:
            results = self.repo.get_market_basket_associations(item_ids, limit)
            
            associations = {}
            for row in results:
                # Store the score as a simple product of confidence and lift
                associations[row.item_b_id] = row.confidence * row.lift
            return associations
        except Exception as e:
            logger.error("Failed to fetch market basket rules", error=str(e))
            return {}
