import os
import sys
import json
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.goal_understanding.models import GoalContext
from app.ai.planning.service import PlanningService

TEST_GOALS = [
    GoalContext(
        goal_type="meal_prep",
        shopping_goal="Meal prep high protein",
        people=1,
        budget=100.0,
        duration="7 days",
        dietary_preferences=["high_protein"],
        brand_preferences=[],
        constraints=[],
        confidence=0.95
    ),
    GoalContext(
        goal_type="weekly_groceries",
        shopping_goal="Vegan family groceries",
        people=4,
        budget=250.0,
        duration="1 week",
        dietary_preferences=["vegan"],
        brand_preferences=[],
        constraints=[],
        confidence=0.98
    ),
    GoalContext(
        goal_type="event",
        shopping_goal="Keto party snacks",
        people=10,
        budget=150.0,
        duration=None,
        dietary_preferences=["keto"],
        brand_preferences=[],
        constraints=[],
        confidence=0.92
    ),
    GoalContext(
        goal_type="restock",
        shopping_goal="Basic staples restock",
        people=2,
        budget=50.0,
        duration="2 weeks",
        dietary_preferences=[],
        brand_preferences=[],
        constraints=[],
        confidence=0.99
    ),
    GoalContext( # Missing budget test
        goal_type="meal_prep",
        shopping_goal="Cook butter chicken",
        people=6,
        budget=None,
        duration=None,
        dietary_preferences=[],
        brand_preferences=[],
        constraints=[],
        confidence=0.96
    )
]

def run_evaluations():
    print(f"Starting planning evaluation of {len(TEST_GOALS)} goals...")
    service = PlanningService()
    
    success_count = 0
    failure_count = 0
    
    for i, goal in enumerate(TEST_GOALS):
        print(f"\n--- Goal {i+1} ---")
        print(f"Type: {goal.goal_type} | Budget: {goal.budget} | Dietary: {goal.dietary_preferences}")
        try:
            plan, metadata = service.plan_goal(goal)
            print("Status: SUCCESS")
            print(f"AI Latency: {metadata['ai_latency_sec']:.2f}s | Rules Latency: {metadata['rules_latency_sec']:.2f}s")
            
            # Print budget allocation
            print("\nAllocations:")
            calculated_sum = sum(cat.estimated_budget for cat in plan.categories)
            for cat in plan.categories:
                print(f"  - [{cat.priority}] {cat.name}: ${cat.estimated_budget:.2f} ({cat.target_quantity})")
                
            print(f"Total Budget Sum: ${calculated_sum:.2f} (Expected: ${plan.total_budget:.2f})")
            
            if abs(calculated_sum - plan.total_budget) > 0.01:
                print("WARNING: Math discrepancy detected in allocation!")
                
            success_count += 1
        except Exception as e:
            print(f"Status: ERROR")
            print(f"Exception: {str(e)}")
            failure_count += 1
            
    print("\n=== EVALUATION SUMMARY ===")
    print(f"Total Goals Tested: {len(TEST_GOALS)}")
    print(f"Successes: {success_count}")
    print(f"Failures: {failure_count}")

if __name__ == "__main__":
    run_evaluations()
