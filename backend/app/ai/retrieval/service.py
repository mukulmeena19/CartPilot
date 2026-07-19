import time
import structlog
from typing import Tuple, Dict, Any
from sqlalchemy.orm import Session
from app.ai.providers.embeddings import get_embedding_provider
from app.ai.planning.models import ShoppingPlan
from app.ai.retrieval.models import RetrievalResult, CategoryRetrievalResult
from app.ai.retrieval.retriever import HybridRetriever

logger = structlog.get_logger(__name__)

class RetrievalService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_provider = get_embedding_provider()
        self.retriever = HybridRetriever(db=self.db, embedding_provider=self.embedding_provider)

    def retrieve_products(self, plan: ShoppingPlan) -> Tuple[RetrievalResult, Dict[str, Any]]:
        start_time = time.time()
        logger.info("Starting product retrieval", num_categories=len(plan.categories))
        
        category_results = []
        total_retrieved = 0
        
        try:
            for allocation in plan.categories:
                # Retrieve top candidates for this budget slice
                candidates = self.retriever.retrieve_for_allocation(
                    allocation=allocation, 
                    goal_assumptions=plan.assumptions
                )
                
                category_results.append(CategoryRetrievalResult(
                    category_name=allocation.name,
                    requested_budget=allocation.estimated_budget,
                    candidates=candidates
                ))
                total_retrieved += len(candidates)
                
            result = RetrievalResult(
                categories=category_results,
                total_candidates=total_retrieved
            )
            
            latency = time.time() - start_time
            logger.info(
                "Retrieval successful",
                latency_sec=latency,
                total_candidates=total_retrieved
            )
            
            return result, {"latency_sec": latency}
            
        except Exception as e:
            logger.error("Retrieval failed", error=str(e))
            raise
