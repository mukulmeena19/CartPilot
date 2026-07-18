import json
from typing import Tuple, Dict, Any
from app.ai.providers.base import LLMProvider
from app.ai.prompts.planning_v1 import PLANNING_SYSTEM_PROMPT_V1
from app.ai.goal_understanding.models import GoalContext
from app.ai.planning.models import AIPlanningInference, ShoppingPlan
from app.ai.planning.rules_engine import RulesEngine
from app.ai.planning.budget_allocator import BudgetAllocator

class Planner:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.rules_engine = RulesEngine()
        self.budget_allocator = BudgetAllocator()

    def generate_plan(self, goal: GoalContext) -> Tuple[ShoppingPlan, Dict[str, Any]]:
        # 1. Prepare context for LLM
        user_prompt = f"Goal Context:\n{goal.model_dump_json()}"
        
        # 2. AI Inference (Semantic weights & Categories)
        inference_result, metadata = self.provider.generate_structured(
            system_prompt=PLANNING_SYSTEM_PROMPT_V1,
            user_prompt=user_prompt,
            response_model=AIPlanningInference
        )
        
        # 3. Rules Engine Execution
        initial_weights = {cat.name: cat.weight for cat in inference_result.categories}
        adjusted_weights = self.rules_engine.apply_dietary_constraints(goal, initial_weights)
        hard_minimums = self.rules_engine.get_hard_minimum_percentages(goal)
        assumptions = self.rules_engine.generate_assumptions(goal)
        
        # 4. Deterministic Budget Allocation
        allocations = self.budget_allocator.allocate(
            categories=inference_result.categories,
            weights=adjusted_weights,
            hard_minimums=hard_minimums,
            total_budget=goal.budget
        )
        
        # 5. Compile Final Shopping Plan
        plan = ShoppingPlan(
            categories=allocations,
            total_budget=goal.budget if goal.budget else 100.0, # 100 acts as a % scale if no budget
            goal_confidence=goal.confidence,
            planning_confidence=inference_result.confidence,
            assumptions=assumptions
        )
        
        return plan, metadata
