from app.ai.verification.models import VerifiedCandidate
from app.ai.memory.models import UserPreferenceContext
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
            # Find if the product name or category implies a preferred brand
            for brand, sig in preferences.brands.items():
                # We would typically use explicit DB fields, using string matching as fallback
                if cand.matched_attributes and brand in cand.matched_attributes:
                    brand_pref = sig
                    break
                elif brand.lower() in cand.product_name.lower():
                    brand_pref = sig
                    break
                    
            if brand_pref:
                # Add bonus proportional to the user's confidence in this brand
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

        return OptimizationTrace(
            product_id=cand.product_id,
            product_name=cand.product_name,
            original_score=base_score,
            final_score=final_score,
            bonuses_applied=bonuses
        )
