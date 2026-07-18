import time
import structlog
from typing import Tuple, Dict, Any
from sqlalchemy.orm import Session
from app.ai.retrieval.models import RetrievalResult
from app.ai.verification.models import VerificationResult, CategoryVerificationResult
from app.ai.verification.verifier import VerificationPipeline

logger = structlog.get_logger(__name__)

class VerificationService:
    def __init__(self, db: Session):
        self.db = db
        self.pipeline = VerificationPipeline(db)

    def verify(self, retrieval_result: RetrievalResult) -> Tuple[VerificationResult, Dict[str, Any]]:
        start_time = time.time()
        logger.info("Starting verification pipeline", total_candidates_in=retrieval_result.total_candidates)
        
        category_results = []
        total_verified = 0
        total_rejected = 0
        
        try:
            for cat_res in retrieval_result.categories:
                # Run the deterministic verification rules
                verified_candidates = self.pipeline.verify_candidates(cat_res.candidates)
                
                # Count stats
                approved = sum(1 for c in verified_candidates if c.verification_status)
                total_verified += approved
                total_rejected += (len(verified_candidates) - approved)
                
                category_results.append(CategoryVerificationResult(
                    category_name=cat_res.category_name,
                    verified_candidates=verified_candidates
                ))
                
            result = VerificationResult(
                categories=category_results,
                total_verified=total_verified,
                total_rejected=total_rejected
            )
            
            latency = time.time() - start_time
            logger.info(
                "Verification pipeline completed",
                latency_sec=latency,
                total_verified=total_verified,
                total_rejected=total_rejected
            )
            
            return result, {"latency_sec": latency}
            
        except Exception as e:
            logger.error("Verification pipeline failed", error=str(e))
            raise
