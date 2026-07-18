from typing import List, Tuple
from app.ai.verification.models import VerifiedCandidate
from app.ai.planning.models import CategoryAllocation
from app.ai.memory.models import UserPreferenceContext
from app.ai.optimization.config import MAX_BUDGET_OVERRIDE_RATIO

class ConstraintEngine:
    @staticmethod
    def apply_hard_constraints(
        candidates: List[VerifiedCandidate],
        allocation: CategoryAllocation,
        preferences: UserPreferenceContext
    ) -> List[Tuple[VerifiedCandidate, str]]: # Returns list of (Candidate, Drop Reason or None)
        """
        Ruthlessly eliminates candidates that violate hard business or user constraints.
        Returns the candidates, keeping track of dropped ones for the OptimizationTrace.
        """
        results = []
        
        # Determine strict budget ceiling for this specific slice
        hard_budget_ceiling = allocation.estimated_budget * MAX_BUDGET_OVERRIDE_RATIO
        
        rejected_ids = set(preferences.rejected_products) if preferences else set()
        
        for vc in candidates:
            cand = vc.candidate
            drop_reason = None
            
            # 1. Budget Constraint
            if cand.price > hard_budget_ceiling:
                drop_reason = f"Exceeds category hard budget ceiling (${cand.price} > ${hard_budget_ceiling:.2f})"
                
            # 2. Hard Rejection Memory Constraint
            elif cand.product_id in rejected_ids:
                drop_reason = "Explicitly rejected in user history"
                
            # 3. Dietary / Allergy Constraint (Stubbed via text matching for now)
            elif preferences and preferences.allergies:
                cand_text = f"{cand.product_name} {cand.category_name}".lower()
                for allergy, sig in preferences.allergies.items():
                    if allergy.lower() in cand_text:
                        drop_reason = f"Violates explicit allergy ({allergy})"
                        break
                        
            results.append((vc, drop_reason))
            
        return results
