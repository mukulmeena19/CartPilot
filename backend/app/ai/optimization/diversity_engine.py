from typing import List, Set
from app.ai.optimization.models import OptimizedCandidate
from app.ai.optimization.config import BRAND_DUPLICATION_PENALTY

class DiversityEngine:
    def __init__(self):
        self.selected_brands: Set[str] = set()
        
    def extract_brand(self, name: str) -> str:
        """Primitive brand extractor for diversity tracking"""
        # In a real DB, cand.brand would be passed directly.
        # Here we just take the first word as a naive brand heuristic if no brand column is mapped in candidate.
        return name.split(" ")[0].lower()

    def apply_diversity_penalty(self, candidate_trace: OptimizedCandidate) -> OptimizedCandidate:
        """
        Softly penalizes items if their brand has already been selected in this cart,
        encouraging brand diversity unless the item's score is overwhelmingly high.
        """
        brand = self.extract_brand(candidate_trace.candidate.candidate.product_name)
        
        if brand in self.selected_brands:
            penalty = BRAND_DUPLICATION_PENALTY
            candidate_trace.final_score -= penalty
            candidate_trace.optimization_trace.final_score -= penalty
            candidate_trace.optimization_trace.penalties_applied.append(
                f"Diversity Penalty (Brand '{brand}' already in cart: -{penalty})"
            )
            
        return candidate_trace
        
    def record_selection(self, candidate_trace: OptimizedCandidate):
        brand = self.extract_brand(candidate_trace.candidate.candidate.product_name)
        self.selected_brands.add(brand)
