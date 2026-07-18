from typing import List, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.ai.retrieval.models import ProductCandidate
from app.ai.verification.models import VerifiedCandidate
from app.ai.verification.candidate_filter import CandidateFilter
from app.ai.verification.inventory_checker import InventoryChecker
from app.ai.verification.pricing_checker import PricingChecker

class VerificationPipeline:
    def __init__(self, db: Session):
        self.db = db

    def verify_candidates(self, candidates: List[ProductCandidate]) -> List[VerifiedCandidate]:
        if not candidates:
            return []
            
        # 1. Deduplicate
        unique_candidates = CandidateFilter.deduplicate(candidates)
        
        # 2. Bulk Data Loading
        activity_map = CandidateFilter.check_activity(self.db, unique_candidates)
        stock_map = InventoryChecker.check_bulk_inventory(self.db, unique_candidates)
        
        verified_results = []
        now = datetime.now(timezone.utc)
        
        for cand in unique_candidates:
            # Defaults
            is_valid = True
            reason = "Valid"
            score = 1.0
            
            is_active = activity_map.get(cand.product_id, False)
            stock_qty = stock_map.get(cand.product_id, 0)
            is_price_valid = PricingChecker.is_price_valid(cand)
            
            # --- Hard Business Rules ---
            if not is_active:
                is_valid = False
                reason = "Product is inactive or discontinued"
                score = 0.0
            elif stock_qty <= 0:
                is_valid = False
                reason = "Out of stock"
                score = 0.0
            elif not is_price_valid:
                is_valid = False
                reason = "Invalid pricing"
                score = 0.0
            else:
                # --- Scoring Adjustments ---
                if stock_qty < 5:
                    score -= 0.2
                    reason = "Valid (Low Stock Warning)"
                    
            verified_results.append(VerifiedCandidate(
                candidate=cand,
                verification_status=is_valid,
                verification_reason=reason,
                stock_available=(stock_qty > 0),
                available_quantity=stock_qty,
                price_verified=is_price_valid,
                merchant_available=True, # Assuming merchant is up if stock exists
                verification_timestamp=now,
                verification_score=max(0.0, score) # Ensure non-negative
            ))
            
        return verified_results
