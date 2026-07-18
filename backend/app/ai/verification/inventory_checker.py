from typing import List, Dict
from sqlalchemy.orm import Session
from app.ai.retrieval.models import ProductCandidate
from app.db.models.inventory import Inventory

class InventoryChecker:
    @staticmethod
    def check_bulk_inventory(db: Session, candidates: List[ProductCandidate]) -> Dict[int, int]:
        """
        Queries the database for inventory levels of multiple products at once.
        Returns a mapping of product_id -> available_quantity.
        Prevents N+1 query vulnerability.
        """
        product_ids = [c.product_id for c in candidates]
        if not product_ids:
            return {}
            
        inventories = db.query(Inventory).filter(Inventory.product_id.in_(product_ids)).all()
        
        # Build mapping. If a product has no inventory record, we assume 0 stock.
        stock_map = {inv.product_id: inv.stock_quantity for inv in inventories}
        
        return stock_map
