from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.repositories.base import BaseRepository
from app.db.models.product import Product, Category

class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: Session):
        super().__init__(Product, db)
        
    def get_category_by_name(self, name: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.name.ilike(f"%{name}%")).first()
        
    def get_active_products(self, category_id: Optional[int] = None) -> List[Product]:
        q = self.db.query(Product).filter(Product.is_active == True)
        if category_id is not None:
            q = q.filter(Product.category_id == category_id)
        return q.all()
