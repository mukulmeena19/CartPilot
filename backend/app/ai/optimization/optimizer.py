from typing import List, Dict, Optional
from app.ai.planning.models import ShoppingPlan
from app.ai.verification.models import VerificationResult, VerifiedCandidate
from app.ai.memory.models import UserPreferenceContext
from app.ai.optimization.models import (
    OptimizedShoppingPlan, 
    OptimizedCategory, 
    OptimizedCandidate, 
    OptimizationTrace
)
from app.ai.optimization.constraint_engine import ConstraintEngine
from app.ai.optimization.scoring_engine import ScoringEngine
from app.ai.optimization.diversity_engine import DiversityEngine

class ShoppingOptimizer:
    def optimize(
        self,
        plan: ShoppingPlan,
        verification_result: VerificationResult,
        preferences: Optional[UserPreferenceContext]
    ) -> OptimizedShoppingPlan:
        """
        The core deterministic algorithm.
        O(C * N log N) where C is categories and N is candidates per category.
        """
        # Map verification results by category for fast lookup
        verif_map: Dict[str, List[VerifiedCandidate]] = {}
        for cat_res in verification_result.categories:
            verif_map[cat_res.category_name] = cat_res.verified_candidates
            
        optimized_categories = []
        total_budget_used = 0.0
        categories_fulfilled = 0
        
        # Instantiate a single diversity engine for the entire cart to track global diversity
        diversity_engine = DiversityEngine()
        
        for allocation in plan.categories:
            candidates = verif_map.get(allocation.name, [])
            
            # 1. Hard Constraints Pass
            constraint_results = ConstraintEngine.apply_hard_constraints(
                candidates, allocation, preferences
            )
            
            valid_candidates = []
            
            # 2. Scoring Pass
            for cand, drop_reason in constraint_results:
                if drop_reason:
                    # We just track it in the trace, don't proceed
                    trace = OptimizationTrace(
                        product_id=cand.candidate.product_id,
                        product_name=cand.candidate.product_name,
                        dropped=True,
                        drop_reason=drop_reason
                    )
                    # We would typically log this trace to observability tools here
                    continue
                    
                trace = ScoringEngine.score_candidate(cand, preferences)
                
                valid_candidates.append(
                    OptimizedCandidate(
                        candidate=cand,
                        final_score=trace.final_score,
                        optimization_trace=trace
                    )
                )
                
            if not valid_candidates:
                # Failed to fulfill this category
                optimized_categories.append(
                    OptimizedCategory(
                        allocation=allocation,
                        selected_items=[],
                        total_cost=0.0
                    )
                )
                continue
                
            # 3. Selection Pass (Greedy Knapsack with Diversity)
            
            # First, sort all valid candidates purely by score
            valid_candidates.sort(key=lambda x: x.final_score, reverse=True)
            
            selected_items = []
            category_cost = 0.0
            
            # Very basic fractional knapsack heuristic
            # We want to fulfill "target_quantity". For simplicity, let's just pick the absolute best 
            # item that fits the budget. If "high" quantity, we might buy 2 of them.
            
            best_item = valid_candidates[0]
            
            # 4. Diversity Pass
            # Penalize the best item if it breaks diversity, and re-sort if necessary.
            # (In a true knapsack we'd evaluate the whole set, but a greedy approach is O(N)).
            best_item = diversity_engine.apply_diversity_penalty(best_item)
            
            # We will just select 1 unit of the best item for the MVP
            # (A real knapsack would fill until allocation.estimated_budget is hit)
            if best_item.candidate.candidate.price <= allocation.estimated_budget * 1.5:
                selected_items.append(best_item)
                category_cost += best_item.candidate.candidate.price
                diversity_engine.record_selection(best_item)
                
            if selected_items:
                categories_fulfilled += 1
                
            total_budget_used += category_cost
            
            optimized_categories.append(
                OptimizedCategory(
                    allocation=allocation,
                    selected_items=selected_items,
                    total_cost=category_cost
                )
            )
            
        success_rate = (categories_fulfilled / len(plan.categories)) * 100 if plan.categories else 0.0
        
        return OptimizedShoppingPlan(
            categories=optimized_categories,
            total_budget_used=total_budget_used,
            total_budget_allocated=plan.total_budget,
            optimization_success_rate=success_rate
        )
