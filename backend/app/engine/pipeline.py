import time
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.engine.models import CandidateScore, RecommendationResponse
from app.engine.retrieval.hybrid import HybridRetriever
from app.engine.constraints import ConstraintFilter
from app.engine.ranking.plugins import ExplainablePluginRanker, NutritionScorePlugin, PopularityScorePlugin, BudgetOptimizerPlugin
from app.engine.ranking.personalization import PersonalizationPlugin
from app.engine.logger import explain_logger
from app.core.embeddings import embedding_service

class RecommendationPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.retriever = HybridRetriever(db)
        self.ranker = ExplainablePluginRanker(
            plugins={
                "nutrition": NutritionScorePlugin(),
                "budget": BudgetOptimizerPlugin(),
                "popularity": PopularityScorePlugin(),
                "personalization": PersonalizationPlugin()
            }
        )

    def run(self, query: str, context: Dict[str, Any], limit: int = 10) -> List[RecommendationResponse]:
        latencies = {}
        
        # 1. Embed Query
        t0 = time.perf_counter()
        embedding = embedding_service.embed_query(query)
        latencies["embed_query"] = time.perf_counter() - t0
        
        # 2. Hybrid Retrieval
        t0 = time.perf_counter()
        candidates = self.retriever.retrieve_candidates(query, embedding, limit=limit*3)
        latencies["hybrid_retrieval"] = time.perf_counter() - t0
        
        # 3. Constraint Filter
        t0 = time.perf_counter()
        filtered_candidates = ConstraintFilter.apply(candidates, context)
        latencies["constraint_filter"] = time.perf_counter() - t0
        
        # 4. Candidate Enrichment
        t0 = time.perf_counter()
        # Mock enrichment (e.g., fetch real-time inventory or personalized prices)
        for c in filtered_candidates:
            c.enriched_data["retrieved_at"] = time.time()
        latencies["candidate_enrichment"] = time.perf_counter() - t0
        
        # 5. Plugin Ranking
        t0 = time.perf_counter()
        ranked_candidates = self.ranker.rank(filtered_candidates, context)
        # Take top K
        final_candidates = ranked_candidates[:limit]
        latencies["plugin_ranking"] = time.perf_counter() - t0
        
        # 6. Explanation Builder & Response DTO
        t0 = time.perf_counter()
        responses = []
        for c in final_candidates:
            # Emit structured explainability log
            explain_logger.log_recommendation(query, c, latencies)
            
            # Map to DTO
            item = c.item
            responses.append(
                RecommendationResponse(
                    id=str(item.id),
                    name=getattr(item, "name", "Unknown"),
                    price=getattr(item, "price", 0.0),
                    image_url=getattr(item, "image_url", None),
                    reasons=c.reasons,
                    final_score=c.final_score
                )
            )
        latencies["explanation_builder"] = time.perf_counter() - t0
        latencies["total_pipeline"] = sum(latencies.values())
        
        return responses
