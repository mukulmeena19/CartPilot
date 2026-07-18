import math
from typing import Dict, List
from app.ai.planning.models import InferredCategory, CategoryAllocation

class BudgetAllocator:
    @staticmethod
    def allocate(
        categories: List[InferredCategory], 
        weights: Dict[str, float], 
        hard_minimums: Dict[str, float], 
        total_budget: float
    ) -> List[CategoryAllocation]:
        """
        Mathematically distributes the budget across categories based on weights,
        respecting hard minimum percentages.
        """
        # If no budget provided, use a dummy scale for planning (e.g., 100 as a percentage scale)
        actual_budget = total_budget if total_budget is not None and total_budget > 0 else 100.0
        
        allocations = []
        remaining_budget = actual_budget
        
        # 1. Enforce hard minimums first
        locked_budgets = {}
        for cat in categories:
            if cat.name in hard_minimums:
                required_amount = actual_budget * hard_minimums[cat.name]
                locked_budgets[cat.name] = required_amount
                remaining_budget -= required_amount
                
        if remaining_budget < 0:
            # Fallback if hard minimums sum to > 100% (shouldn't happen with correct config)
            remaining_budget = 0
            
        # 2. Calculate remaining weight pool for remaining budget
        total_remaining_weight = 0.0
        for cat in categories:
            if cat.name not in locked_budgets:
                total_remaining_weight += weights.get(cat.name, 1.0)
                
        # 3. Distribute remaining budget
        final_allocations = {}
        for cat in categories:
            if cat.name in locked_budgets:
                final_allocations[cat.name] = locked_budgets[cat.name]
            else:
                w = weights.get(cat.name, 1.0)
                share = (w / total_remaining_weight) * remaining_budget if total_remaining_weight > 0 else 0
                final_allocations[cat.name] = share
                
        # 4. Handle rounding errors to ensure exact sum matches total_budget
        allocated_sum = sum(final_allocations.values())
        diff = actual_budget - allocated_sum
        
        # Assign diff to highest weight category to perfectly balance
        if final_allocations and abs(diff) > 0.001:
            highest_cat = max(final_allocations, key=lambda k: weights.get(k, 0))
            final_allocations[highest_cat] += diff
            
        # 5. Build Final Objects
        # Sort by final allocation (descending) to determine priority
        sorted_cats = sorted(categories, key=lambda c: final_allocations[c.name], reverse=True)
        
        for i, cat in enumerate(sorted_cats):
            allocations.append(CategoryAllocation(
                name=cat.name,
                priority=i + 1,
                estimated_budget=round(final_allocations[cat.name], 2),
                target_quantity=cat.target_quantity,
                reasoning=cat.reasoning
            ))
            
        return allocations
