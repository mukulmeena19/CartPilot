from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.models.product import Product
from app.db.models.category import Category
from app.ai.planning.models import CategoryAllocation
from app.ai.retrieval.models import ProductCandidate
from app.ai.retrieval.config import TOP_K, SIMILARITY_THRESHOLD, MAX_PRICE_MULTIPLIER
from app.ai.providers.embeddings import EmbeddingProvider

class HybridRetriever:
    def __init__(self, db: Session, embedding_provider: EmbeddingProvider):
        self.db = db
        self.embedding_provider = embedding_provider

    def retrieve_for_allocation(self, allocation: CategoryAllocation, goal_assumptions: List[str] = None) -> List[ProductCandidate]:
        # 1. Search Query Builder
        # Construct a semantic query to embed based on the AI's abstract allocation
        query_text = f"{allocation.name} groceries. {allocation.target_quantity} quantity. {allocation.reasoning}"
        
        # 2. Embedding Generation
        # Convert the query to a vector
        try:
            query_vector = self.embedding_provider.generate_embeddings([query_text])[0]
        except Exception:
            # Fallback to empty if API fails, relying purely on metadata filters
            query_vector = None

        candidates = []
        
        # 3. Hybrid Search
        # We query the DB filtering by explicit category name AND semantic similarity
        # First, try to resolve the category name to a DB Category ID
        db_category = self.db.query(Category).filter(Category.name.ilike(f"%{allocation.name}%")).first()
        
        # Base query (only active items)
        q = self.db.query(Product).filter(Product.is_active == True)
        
        # Soft-filter by category if we found a match (not strictly required if semantic is strong enough, 
        # but requested in architecture for hybrid safety)
        if db_category:
            q = q.filter(Product.category_id == db_category.id)
            
        # Execute Query
        db_products = q.all()
        
        # 4. In-memory scoring and filtering
        # Note: In a massive scale DB, this pgvector cosine similarity would be pushed down to SQL:
        # q = q.order_by(Product.embedding.cosine_distance(query_vector)).limit(TOP_K)
        # However, for hybrid filtering with price outlier logic on a small/medium catalog, 
        # doing it via explicit calculation or hybrid SQL works.
        # Since we use pgvector, let's use the DB capability if vector exists.
        
        if query_vector and db_products:
            # We construct a new query using the SQL cosine distance operator <=>
            # Postgres <=> returns distance, so similarity = 1 - distance
            # Requires pgvector extension enabled.
            # Using raw text for array formatting in SQLAlchemy for pgvector
            vector_str = "[" + ",".join(map(str, query_vector)) + "]"
            
            # Re-build query to order by vector distance
            q_vector = self.db.query(Product, Product.embedding.cosine_distance(vector_str).label("distance"))
            q_vector = q_vector.filter(Product.is_active == True)
            if db_category:
                q_vector = q_vector.filter(Product.category_id == db_category.id)
                
            q_vector = q_vector.filter(Product.embedding.is_not(None))
            # Get a larger pool to filter outliers
            results = q_vector.order_by("distance").limit(TOP_K * 3).all()
            
            for prod, distance in results:
                similarity = 1.0 - distance
                if similarity >= SIMILARITY_THRESHOLD:
                    candidates.append((prod, similarity, "hybrid_vector"))
        else:
            # Fallback: No vector or API failed. Just use category metadata.
            for prod in db_products[:TOP_K*3]:
                candidates.append((prod, 0.5, "metadata_fallback"))
                
        # 5. Price Outlier Filter
        # Exclude items that are absurdly expensive compared to the requested slice.
        max_allowed_price = allocation.estimated_budget * MAX_PRICE_MULTIPLIER
        
        valid_candidates = []
        for prod, sim, method in candidates:
            if prod.price <= max_allowed_price:
                # 6. Candidate Merge mapping
                cat_name = prod.category.name if prod.category else "Unknown"
                valid_candidates.append(ProductCandidate(
                    product_id=prod.id,
                    product_name=prod.name,
                    category_name=cat_name,
                    price=prod.price,
                    similarity_score=round(sim, 4),
                    retrieval_method=method,
                    embedding_model=prod.embedding_model or "none"
                ))
                
        # Sort by similarity and return TOP_K
        valid_candidates.sort(key=lambda x: x.similarity_score, reverse=True)
        return valid_candidates[:TOP_K]
