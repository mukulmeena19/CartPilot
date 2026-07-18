import os
import sys
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.planning.models import CategoryAllocation
from app.ai.retrieval.models import ProductCandidate
from app.ai.verification.models import VerifiedCandidate
from app.ai.optimization.models import OptimizedShoppingPlan, OptimizedCategory, OptimizedCandidate, OptimizationTrace
from app.ai.explainability.service import ExplainabilityService

MOCK_OPTIMIZED_PLAN = OptimizedShoppingPlan(
    categories=[
        OptimizedCategory(
            allocation=CategoryAllocation(
                name="Dairy",
                priority=1,
                estimated_budget=10.0,
                target_quantity="medium",
                reasoning="Required"
            ),
            selected_items=[
                OptimizedCandidate(
                    candidate=VerifiedCandidate(
                        candidate=ProductCandidate(
                            product_id=2,
                            product_name="Amul Milk",
                            category_name="Dairy",
                            price=4.00,
                            similarity_score=0.85,
                            embedding_model="test",
                            matched_attributes=["Amul"]
                        ),
                        verification_status=True,
                        verification_reason="Valid",
                        stock_available=True,
                        available_quantity=5,
                        price_verified=True,
                        merchant_available=True,
                        verification_timestamp=datetime.now(timezone.utc),
                        verification_score=1.0
                    ),
                    final_score=1.2,
                    optimization_trace=OptimizationTrace(
                        product_id=2,
                        product_name="Amul Milk",
                        original_score=0.9,
                        final_score=1.2,
                        bonuses_applied=["Brand Affinity (Amul: +0.30)", "Dietary Alignment (Vegetarian: +0.10)"]
                    )
                )
            ],
            total_cost=4.00
        )
    ],
    total_budget_used=4.00,
    total_budget_allocated=10.00,
    optimization_success_rate=100.0
)

def run_evaluations():
    print("Starting explainability evaluation...\n")
    service = ExplainabilityService()
    
    try:
        res, metadata = service.explain_plan(MOCK_OPTIMIZED_PLAN)
        
        for cat in res.categories:
            print(f"=== Category: {cat.category_name} ===")
            for item in cat.selected_items:
                print(item.explanation_text)
                print("\nInternal Rules Triggered:", item.supporting_rules)
                print("-" * 40)
                
        print(f"\nLatency: {metadata['latency_sec']:.4f}s")
                
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    run_evaluations()
