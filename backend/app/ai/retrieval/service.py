import time
import structlog
from typing import Tuple, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.ai.providers.embeddings import get_embedding_provider
from app.ai.planning.models import ShoppingPlan
from app.ai.retrieval.models import RetrievalResult, CategoryRetrievalResult
from app.ai.retrieval.retriever import HybridRetriever
from app.ai.goal_understanding.models import GoalContext
from app.db.models.knowledge import Ingredient
from app.knowledge.service import KnowledgeService

logger = structlog.get_logger(__name__)

class RetrievalService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_provider = get_embedding_provider()
        self.retriever = HybridRetriever(db=self.db, embedding_provider=self.embedding_provider)
        self.knowledge_service = KnowledgeService(db=self.db)

    def _resolve_ingredient_ids(self, names: List[str]) -> List[int]:
        ids = []
        for name in names:
            ingredient = self.db.query(Ingredient).filter(Ingredient.name.ilike(f"%{name}%")).first()
            if ingredient:
                ids.append(ingredient.id)
            else:
                logger.warning("Ingredient name did not resolve to ID, skipping expansion", ingredient_name=name)
        return ids

    def retrieve_products(self, plan: ShoppingPlan, domain: str = "grocery", goal_context: GoalContext = None) -> Tuple[RetrievalResult, Dict[str, Any]]:
        start_time = time.time()
        logger.info("Starting product retrieval", num_categories=len(plan.categories), domain=domain)
        
        category_results = []
        total_retrieved = 0
        
        try:
            # Ingredient expansion for grocery domain
            expanded_terms = []
            if domain == "grocery" and goal_context:
                # Extract potential ingredient names from goal context (e.g. from shopping_goal or constraints)
                # In a real system, we'd parse this better, but we'll use words from the goal.
                words = [w for w in goal_context.shopping_goal.split() if len(w) > 3]
                ingredient_ids = self._resolve_ingredient_ids(words)
                if ingredient_ids:
                    expanded_ids = self.knowledge_service.expand_ingredients(ingredient_ids)
                    if expanded_ids:
                        expanded_ingredients = self.db.query(Ingredient).filter(Ingredient.id.in_(expanded_ids)).all()
                        expanded_terms = [i.name for i in expanded_ingredients]
                        logger.info("Expanded ingredients", expanded_terms=expanded_terms)

            assumptions = plan.assumptions + expanded_terms

            for allocation in plan.categories:
                # Retrieve top candidates for this budget slice
                candidates = self.retriever.retrieve_for_allocation(
                    allocation=allocation, 
                    goal_assumptions=assumptions,
                    domain=domain
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
