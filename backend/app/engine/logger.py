import json
import logging
from typing import Dict, Any
from app.engine.models import CandidateScore

logger = logging.getLogger("cartpilot.engine.explainability")

class ExplainabilityLogger:
    @staticmethod
    def log_recommendation(
        query: str, 
        candidate: CandidateScore, 
        latencies: Dict[str, float]
    ):
        """
        Logs a structured explainability and performance trace for a candidate.
        """
        log_data = {
            "query": query,
            "candidate_id": candidate.candidate_id,
            "scores": {
                "semantic": round(candidate.semantic_score, 4),
                "fts": round(candidate.fts_score, 4),
                "nutrition": round(candidate.nutrition_score, 4),
                "budget": round(candidate.budget_score, 4),
                "personalization": round(candidate.personalization_score, 4),
                "popularity": round(candidate.popularity_score, 4),
                "final": round(candidate.final_score, 4),
            },
            "reasons": candidate.reasons,
            "latencies_ms": {k: round(v * 1000, 2) for k, v in latencies.items()}
        }
        
        # In a real setup, we might push this to DataDog/ELK.
        # For now, structured JSON to stdout is perfect.
        logger.info(json.dumps(log_data))

explain_logger = ExplainabilityLogger()
