"""
Hybrid Retrieval Engine.
Combines pgvector semantic search with FTS and strict metadata filters.
"""
from __future__ import annotations

import logging
import math
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, String, cast

from app.db.models.product import Product
from app.db.models.restaurant import Restaurant
from app.core.config import settings
from app.engine.models import CandidateScore

logger = logging.getLogger(__name__)

class SemanticRetriever:
    def __init__(self, db: Session):
        self.db = db

    def retrieve_products(self, embedding: List[float], limit: int = 50) -> List[Tuple[Product, float]]:
        if not embedding:
            return []
            
        vector_str = "[" + ",".join(map(str, embedding)) + "]"
        distance = Product.embedding.cosine_distance(vector_str).label("distance")
        
        q = self.db.query(Product, distance).filter(Product.embedding.is_not(None))
        q = q.filter(Product.is_active == True)
            
        results = q.order_by("distance").limit(limit).all()
        # Cosine distance to similarity (1 - distance)
        return [(prod, max(0.0, 1.0 - float(dist))) for prod, dist in results]


class FTSRetriever:
    def __init__(self, db: Session):
        self.db = db

    def retrieve_products(self, query: str, limit: int = 50) -> List[Tuple[Product, float]]:
        if not query:
            return []
            
        # websearch_to_tsquery for natural language handling
        tsvector = func.to_tsvector('english', cast(Product.name, String) + ' ' + func.coalesce(cast(Product.description, String), ''))
        tsquery = func.websearch_to_tsquery('english', query)
        rank = func.ts_rank(tsvector, tsquery).label('rank')
        
        q = self.db.query(Product, rank).filter(tsvector.op('@@')(tsquery))
        q = q.filter(Product.is_active == True)
            
        results = q.order_by(rank.desc()).limit(limit).all()
        
        # We need to normalize rank. Typically ts_rank is unbounded (usually < 1.0 but can be higher).
        # We'll apply a soft normalization
        normalized_results = []
        for prod, r in results:
            # simple normalization: 1 - e^(-rank) scales rank into [0, 1) smoothly
            norm_score = 1.0 - math.exp(-float(r))
            normalized_results.append((prod, norm_score))
            
        return normalized_results


class HybridRetriever:
    def __init__(self, db: Session):
        self.db = db
        self.semantic = SemanticRetriever(db)
        self.fts = FTSRetriever(db)

    def retrieve_candidates(
        self, 
        query: str, 
        embedding: List[float], 
        limit: int = 50
    ) -> List[CandidateScore]:
        """
        Retrieves products using a combination of vector similarity and exact match filters,
        returning initialized CandidateScore objects.
        """
        # Overfetch initially before constraints
        fetch_limit = limit * 2
        
        semantic_res = self.semantic.retrieve_products(embedding, limit=fetch_limit)
        fts_res = self.fts.retrieve_products(query, limit=fetch_limit)
        
        # Merge into CandidateScore objects
        candidates: Dict[str, CandidateScore] = {}
        
        for item, score in semantic_res:
            c_id = str(item.id)
            if c_id not in candidates:
                candidates[c_id] = CandidateScore(candidate_id=c_id, item=item)
            candidates[c_id].semantic_score = score
            
        for item, score in fts_res:
            c_id = str(item.id)
            if c_id not in candidates:
                candidates[c_id] = CandidateScore(candidate_id=c_id, item=item)
            candidates[c_id].fts_score = score
            
        # We don't apply weights yet! Weights are applied in the ranking stage or we can pre-calculate a base score
        # Actually, let's calculate the combined base score here to sort before constraints.
        
        semantic_w = getattr(settings, "RETRIEVAL_SEMANTIC_WEIGHT", 0.7)
        fts_w = getattr(settings, "RETRIEVAL_FTS_WEIGHT", 0.3)
        
        for c in candidates.values():
            # Base final score before plugins
            c.final_score = (c.semantic_score * semantic_w) + (c.fts_score * fts_w)
            
        # Sort and take top fetch_limit to send to the constraint pipeline
        sorted_candidates = sorted(list(candidates.values()), key=lambda x: x.final_score, reverse=True)
        return sorted_candidates[:fetch_limit]
