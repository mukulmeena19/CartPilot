from typing import Dict
from app.ai.goal_understanding.models import GoalContext
from app.ai.planning.config import DIETARY_CONSTRAINTS

class RulesEngine:
    @staticmethod
    def apply_dietary_constraints(goal: GoalContext, weights: Dict[str, float]) -> Dict[str, float]:
        """
        Adjusts the AI's semantic weights based on hard business rules for dietary preferences.
        """
        # Copy to avoid mutating original
        adjusted_weights = dict(weights)
        
        # We look for matches in the user's dietary preferences
        for pref in goal.dietary_preferences:
            pref_normalized = pref.lower().replace("-", "_").replace(" ", "_")
            if pref_normalized in DIETARY_CONSTRAINTS:
                constraints = DIETARY_CONSTRAINTS[pref_normalized]
                # Boost weights of required categories proportionally
                # (Actual percentages are handled in budget_allocator, 
                # here we just ensure the weights reflect the high priority)
                for cat, min_percent in constraints.items():
                    if cat not in adjusted_weights:
                        adjusted_weights[cat] = 5.0 # default mid weight
                    
                    # Boost by the percentage severity
                    boost_factor = 1.0 + min_percent
                    adjusted_weights[cat] *= boost_factor
                    
        return adjusted_weights
        
    @staticmethod
    def get_hard_minimum_percentages(goal: GoalContext) -> Dict[str, float]:
        """
        Returns a dictionary of category to minimum budget percentage.
        """
        minimums = {}
        for pref in goal.dietary_preferences:
            pref_normalized = pref.lower().replace("-", "_").replace(" ", "_")
            if pref_normalized in DIETARY_CONSTRAINTS:
                for cat, min_percent in DIETARY_CONSTRAINTS[pref_normalized].items():
                    if cat not in minimums or min_percent > minimums[cat]:
                        minimums[cat] = min_percent
        return minimums

    @staticmethod
    def generate_assumptions(goal: GoalContext) -> list[str]:
        assumptions = []
        if not goal.budget:
            assumptions.append("No budget specified; assuming generic estimation (e.g. ₹5000 default).")
        return assumptions
