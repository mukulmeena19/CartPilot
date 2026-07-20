from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.models.product import Product
from app.db.models.category import Category
from app.db.models.restaurant import MenuItem
from app.ai.planning.models import CategoryAllocation
from app.ai.retrieval.models import ProductCandidate
from app.ai.retrieval.config import TOP_K, SIMILARITY_THRESHOLD, MAX_PRICE_MULTIPLIER
from app.ai.providers.embeddings import EmbeddingProvider

class HybridRetriever:
    def __init__(self, db: Session, embedding_provider: EmbeddingProvider):
        self.db = db
        self.embedding_provider = embedding_provider

    def retrieve_for_allocation(self, allocation: CategoryAllocation, goal_assumptions: List[str] = None, domain: str = "grocery") -> List[ProductCandidate]:
        # 1. Search Query Builder
        # Construct a semantic query to embed based on the AI's abstract allocation
        assumptions_str = " ".join(goal_assumptions) if goal_assumptions else ""
        query_text = f"{allocation.name} {'menu items' if domain == 'food' else 'groceries'}. {allocation.target_quantity} quantity. {allocation.reasoning} {assumptions_str}"
        
        # 2. Embedding Generation
        try:
            query_vector = self.embedding_provider.generate_embeddings([query_text])[0]
        except Exception:
            query_vector = None

        candidates = []
        
        # 3. Hybrid Search
        if domain == "food":
            q = self.db.query(MenuItem).filter(MenuItem.is_available == True)
            db_category = None
            # Could filter by cuisine here if we parsed it into allocation.name
            # For now just use semantic search over all menu items
        else:
            db_category = self.db.query(Category).filter(Category.name.ilike(f"%{allocation.name}%")).first()
            q = self.db.query(Product).filter(Product.is_active == True)
            if db_category:
                q = q.filter(Product.category_id == db_category.id)
            
        # Execute Base Query
        db_items = q.all()
        
        # 4. In-memory scoring and filtering
        if query_vector and db_items:
            vector_str = "[" + ",".join(map(str, query_vector)) + "]"
            
            if domain == "food":
                q_vector = self.db.query(MenuItem, MenuItem.embedding.cosine_distance(vector_str).label("distance"))
                q_vector = q_vector.filter(MenuItem.is_available == True)
                q_vector = q_vector.filter(MenuItem.embedding.is_not(None))
            else:
                q_vector = self.db.query(Product, Product.embedding.cosine_distance(vector_str).label("distance"))
                q_vector = q_vector.filter(Product.is_active == True)
                if db_category:
                    q_vector = q_vector.filter(Product.category_id == db_category.id)
                q_vector = q_vector.filter(Product.embedding.is_not(None))
                
            results = q_vector.order_by("distance").limit(TOP_K * 3).all()
            
            for item, distance in results:
                similarity = 1.0 - distance
                if similarity >= SIMILARITY_THRESHOLD:
                    candidates.append((item, similarity, "hybrid_vector"))
        else:
            # Fallback
            for item in db_items[:TOP_K*3]:
                candidates.append((item, 0.5, "metadata_fallback"))
                
        # 5. Price Outlier Filter
        max_allowed_price = allocation.estimated_budget * MAX_PRICE_MULTIPLIER
        
        valid_candidates = []
        for item, sim, method in candidates:
            if item.price <= max_allowed_price:
                # 6. Candidate Merge mapping
                if domain == "food":
                    cat_name = item.category or item.cuisine or "Menu Item"
                    brand = item.restaurant.name if item.restaurant else None
                else:
                    cat_name = item.category.name if item.category else "Unknown"
                    brand = None
                    
                valid_candidates.append(ProductCandidate(
                    product_id=item.id,
                    product_name=item.name,
                    category_name=cat_name,
                    brand=brand,
                    price=item.price,
                    similarity_score=round(sim, 4),
                    retrieval_method=method,
                    embedding_model=getattr(item, "embedding_model", None) or "none"
                ))
                
        # Sort by similarity and return TOP_K
        valid_candidates.sort(key=lambda x: x.similarity_score, reverse=True)
        return valid_candidates[:TOP_K]
