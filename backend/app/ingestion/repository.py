from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.db.models.product import Product
from app.db.models.category import Category
from datetime import datetime, timezone

class Repository:
    def __init__(self, db: Session):
        self.db = db
        # Cache categories to avoid constant lookups
        self.category_cache = {}

    def _get_or_create_category(self, category_name: str) -> int:
        if category_name in self.category_cache:
            return self.category_cache[category_name]
            
        category = self.db.query(Category).filter(Category.name == category_name).first()
        if not category:
            category = Category(name=category_name, description=f"{category_name} items")
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            
        self.category_cache[category_name] = category.id
        return category.id

    def upsert_products(self, items: List[Dict[str, Any]]):
        if not items:
            return

        values_to_insert = []
        for item in items:
            cat_id = self._get_or_create_category(item["category_name"])
            values_to_insert.append({
                "id": str(item["id"]), # ensure string
                "name": item["name"],
                "brand": item["brand"],
                "category_id": cat_id,
                "price": item["price"],
                "unit": item["unit"],
                "nutrition": item["nutrition"],
                "image_url": item["image_url"],
                "description": item["description"],
                "embedding": item["embedding"],
                "embedding_model": item.get("embedding_model"),
                "embedding_version": item.get("embedding_version"),
                "embedding_generated_at": datetime.now(timezone.utc)
            })

        stmt = insert(Product).values(values_to_insert)
        
        # Idempotency: on conflict do update
        update_dict = {
            "name": stmt.excluded.name,
            "brand": stmt.excluded.brand,
            "category_id": stmt.excluded.category_id,
            "price": stmt.excluded.price,
            "unit": stmt.excluded.unit,
            "nutrition": stmt.excluded.nutrition,
            "image_url": stmt.excluded.image_url,
            "description": stmt.excluded.description,
            "embedding": stmt.excluded.embedding,
            "embedding_model": stmt.excluded.embedding_model,
            "embedding_version": stmt.excluded.embedding_version,
            "embedding_generated_at": stmt.excluded.embedding_generated_at,
            "updated_at": func.now() if hasattr(func, 'now') else datetime.now(timezone.utc)
        }
        
        from sqlalchemy.sql import func

        stmt = stmt.on_conflict_do_update(
            index_elements=['id'],
            set_=update_dict
        )
        
        self.db.execute(stmt)
        self.db.commit()
