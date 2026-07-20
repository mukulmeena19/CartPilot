from app.ai.verification.models import VerifiedCandidate
from app.ai.memory.models import UserPreferenceContext
from app.ai.planning.models import CategoryAllocation
from app.ai.optimization.models import OptimizationTrace
from app.ai.optimization.config import (
    WEIGHT_SEMANTIC_SIMILARITY,
    WEIGHT_VERIFICATION_SCORE,
    WEIGHT_PREFERENCE_BONUS
)

class ScoringEngine:
    @staticmethod
    def score_candidate(
        vc: VerifiedCandidate, 
        allocation: CategoryAllocation,
        preferences: UserPreferenceContext
    ) -> OptimizationTrace:
        """
        Computes a unified multi-objective score for a verified candidate,
        applying mathematical bonuses based on the user's preference context.
        """
        cand = vc.candidate
        
        # Base mathematical scores
        sim_score = cand.similarity_score * WEIGHT_SEMANTIC_SIMILARITY
        ver_score = vc.verification_score * WEIGHT_VERIFICATION_SCORE
        
        base_score = sim_score + ver_score
        final_score = base_score
        
        bonuses = []
        
        # Preference Bonus calculation
        if preferences:
            # 1. Brand Affinity Bonus
            brand_pref = None
            for brand, sig in preferences.brands.items():
                if cand.matched_attributes and brand in cand.matched_attributes:
                    brand_pref = sig
                    break
                elif brand.lower() in cand.product_name.lower():
                    brand_pref = sig
                    break
                    
            if brand_pref:
                bonus = brand_pref.confidence * WEIGHT_PREFERENCE_BONUS
                final_score += bonus
                bonuses.append(f"Brand Affinity ({brand}: +{bonus:.2f})")
                
            # 2. Dietary Alignment Bonus
            dietary_pref = None
            for diet, sig in preferences.dietary.items():
                if diet.lower() in cand.product_name.lower() or diet.lower() in cand.category_name.lower():
                    dietary_pref = sig
                    break
                    
            if dietary_pref:
                bonus = dietary_pref.confidence * WEIGHT_PREFERENCE_BONUS
                final_score += bonus
                bonuses.append(f"Dietary Alignment ({diet}: +{bonus:.2f})")

        # 3. Nutrition/Protein Bonus
        protein_target = preferences.protein_target if preferences and hasattr(preferences, "protein_target") else None
        if protein_target and hasattr(cand, "nutrition") and cand.nutrition:
            protein = cand.nutrition.get("protein", 0.0)
            if protein >= protein_target:
                bonus = 1.0 * WEIGHT_PREFERENCE_BONUS
                final_score += bonus
                bonuses.append(f"High in protein ({protein}g: +{bonus:.2f})")
            elif protein >= protein_target / 2:
                bonus = 0.5 * WEIGHT_PREFERENCE_BONUS
                final_score += bonus
                bonuses.append(f"Good source of protein (+{bonus:.2f})")

        # 4. Budget Optimizer
        target_budget = allocation.estimated_budget
        if target_budget > 0 and hasattr(cand, "price") and cand.price is not None:
            price = cand.price
            if price <= target_budget * 0.5:
                bonus = 1.0 * WEIGHT_PREFERENCE_BONUS
                final_score += bonus
                bonuses.append(f"Great value (under budget: +{bonus:.2f})")
            elif price <= target_budget:
                bonus = 0.7 * WEIGHT_PREFERENCE_BONUS
                final_score += bonus
                bonuses.append(f"Within budget (+{bonus:.2f})")

        # 5. Popularity Bonus
        rating = getattr(cand, "rating", 4.0) or 4.0
        norm_rating = max(0.0, min(1.0, (rating - 1) / 4.0))
        bonus = norm_rating * (WEIGHT_PREFERENCE_BONUS * 0.5)
        final_score += bonus
        if norm_rating >= 0.8:
            bonuses.append(f"Highly rated (+{bonus:.2f})")

        return OptimizationTrace(
            product_id=cand.product_id,
            product_name=cand.product_name,
            original_score=base_score,
            final_score=final_score,
            bonuses_applied=bonuses
        )
