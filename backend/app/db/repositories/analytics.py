from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Tuple
from app.db.repositories.base import BaseRepository
from app.db.models.analytics import TrendSnapshot, MarketBasketAssociation

class AnalyticsRepository(BaseRepository[TrendSnapshot]):
    def __init__(self, db: Session):
        super().__init__(TrendSnapshot, db)
        
    def get_top_trending_products(self, limit: int = 10) -> List[Tuple[int, int]]:
        return self.db.query(
            TrendSnapshot.entity_id, 
            func.sum(TrendSnapshot.score).label('total_score')
        ).filter(TrendSnapshot.entity_type == 'product')\
         .group_by(TrendSnapshot.entity_id)\
         .order_by(func.sum(TrendSnapshot.score).desc())\
         .limit(limit)\
         .all()
         
    def get_top_trending_cuisines(self, limit: int = 5) -> List[Tuple[str, int]]:
        return self.db.query(
            TrendSnapshot.entity_id, 
            func.sum(TrendSnapshot.score).label('total_score')
        ).filter(TrendSnapshot.entity_type == 'cuisine')\
         .group_by(TrendSnapshot.entity_id)\
         .order_by(func.sum(TrendSnapshot.score).desc())\
         .limit(limit)\
         .all()
         
    def get_market_basket_associations(self, item_ids: List[int], limit: int = 5) -> List[MarketBasketAssociation]:
        return self.db.query(MarketBasketAssociation)\
            .filter(MarketBasketAssociation.item_a_id.in_(item_ids))\
            .order_by(MarketBasketAssociation.confidence.desc(), MarketBasketAssociation.lift.desc())\
            .limit(limit)\
            .all()
