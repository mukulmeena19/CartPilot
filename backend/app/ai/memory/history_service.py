from sqlalchemy.orm import Session
from app.db.models.order import Order
from app.db.models.cart import Cart

class HistoryService:
    @staticmethod
    def get_purchase_history(db: Session, user_id: int, limit: int = 50):
        """
        Extracts recent orders. This would be used in future iterations 
        to run background batch jobs to infer preferences.
        """
        # Returns orders. In a real system, we would join order_items.
        return db.query(Order).filter(Order.user_id == user_id)\
            .order_by(Order.created_at.desc()).limit(limit).all()
            
    @staticmethod
    def record_rejected_product(db: Session, user_id: int, product_id: int):
        """
        Called when a user explicitly rejects an item from their generated cart.
        The service layer will hook this into the extractor.
        """
        pass
