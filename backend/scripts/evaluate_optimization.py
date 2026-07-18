import os
import sys
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.planning.models import ShoppingPlan, CategoryAllocation
from app.ai.retrieval.models import ProductCandidate
from app.ai.verification.models import VerificationResult, CategoryVerificationResult, VerifiedCandidate
from app.ai.memory.models import UserPreferenceContext, PreferenceSignal
from app.ai.optimization.service import OptimizationService

# Mock Planning (Milestone 5)
MOCK_PLAN = ShoppingPlan(
    categories=[
        CategoryAllocation(
            name="Dairy",
            priority=1,
            estimated_budget=10.0,
            target_quantity="medium",
            reasoning="Required"
        )
    ],
    total_budget=10.0,
    goal_confidence=1.0,
    planning_confidence=1.0,
    assumptions=[]
)

# Mock Verification (Milestone 7)
MOCK_VERIFICATION = VerificationResult(
    categories=[
        CategoryVerificationResult(
            category_name="Dairy",
            verified_candidates=[
                VerifiedCandidate(
                    candidate=ProductCandidate(
                        product_id=1,
                        product_name="Generic Milk",
                        category_name="Dairy",
                        price=3.00,
                        similarity_score=0.85, # Highly similar
                        embedding_model="test"
                    ),
                    verification_status=True,
                    verification_reason="Valid",
                    stock_available=True,
                    available_quantity=10,
                    price_verified=True,
                    merchant_available=True,
                    verification_timestamp=datetime.now(timezone.utc),
                    verification_score=1.0
                ),
                VerifiedCandidate(
                    candidate=ProductCandidate(
                        product_id=2,
                        product_name="Amul Milk",
                        category_name="Dairy",
                        price=4.00, # More expensive
                        similarity_score=0.80, # Slightly less semantically similar
                        embedding_model="test"
                    ),
                    verification_status=True,
                    verification_reason="Valid",
                    stock_available=True,
                    available_quantity=5,
                    price_verified=True,
                    merchant_available=True,
                    verification_timestamp=datetime.now(timezone.utc),
                    verification_score=0.8 # Penalty for low stock
                )
            ]
        )
    ],
    total_verified=2,
    total_rejected=0
)

# Mock Memory (Milestone 8)
MOCK_PREFS = UserPreferenceContext(
    brands={
        "Amul": PreferenceSignal(value="Amul", confidence=1.0, source="explicit")
    }
)

def run_evaluations():
    print("Starting optimization evaluation...")
    service = OptimizationService()
    
    try:
        # Without Preferences (Should pick Generic Milk because it's cheaper & more similar)
        print("\n=== RUN 1: NO PREFERENCES ===")
        res1, _ = service.optimize_cart(MOCK_PLAN, MOCK_VERIFICATION, None)
        for cat in res1.categories:
            print(f"Category: {cat.allocation.name}")
            if cat.selected_items:
                winner = cat.selected_items[0]
                print(f"  Selected: {winner.candidate.candidate.product_name} | Final Score: {winner.final_score:.2f}")
                print(f"  Trace: {winner.optimization_trace.bonuses_applied}")
            else:
                print("  Selected: None")
                
        # With Preferences (Should pick Amul Milk because of 1.0 confidence brand bonus)
        print("\n=== RUN 2: WITH BRAND PREFERENCE ===")
        res2, _ = service.optimize_cart(MOCK_PLAN, MOCK_VERIFICATION, MOCK_PREFS)
        for cat in res2.categories:
            print(f"Category: {cat.allocation.name}")
            if cat.selected_items:
                winner = cat.selected_items[0]
                print(f"  Selected: {winner.candidate.candidate.product_name} | Final Score: {winner.final_score:.2f}")
                print(f"  Trace: {winner.optimization_trace.bonuses_applied}")
            else:
                print("  Selected: None")
                
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    run_evaluations()
