from typing import List
from app.ai.retrieval.models import ProductCandidate
from sqlalchemy.orm import Session
from app.db.models.product import Product

class CandidateFilter:
    @staticmethod
    def deduplicate(candidates: List[ProductCandidate]) -> List[ProductCandidate]:
        seen = set()
        unique = []
        for c in candidates:
            if c.product_id not in seen:
                seen.add(c.product_id)
                unique.append(c)
        return unique

    @staticmethod
    def check_activity(db: Session, candidates: List[ProductCandidate]) -> dict[int, bool]:
        """
        Returns a mapping of product_id -> is_active.
        Executes a single bulk query to avoid N+1.
        """
        product_ids = [c.product_id for c in candidates]
        if not product_ids:
            return {}
            
        products = db.query(Product.id, Product.is_active).filter(Product.id.in_(product_ids)).all()
        return {p_id: is_active for p_id, is_active in products}
