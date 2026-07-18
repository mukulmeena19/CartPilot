import os
import sys
import json
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.ai.planning.models import ShoppingPlan, CategoryAllocation
from app.ai.retrieval.service import RetrievalService

# Create a mock shopping plan for evaluation
TEST_PLAN = ShoppingPlan(
    categories=[
        CategoryAllocation(
            name="Produce",
            priority=1,
            estimated_budget=15.0,
            target_quantity="high",
            reasoning="Required for base meal prep"
        ),
        CategoryAllocation(
            name="Dairy",
            priority=2,
            estimated_budget=8.0,
            target_quantity="medium",
            reasoning="Butter and milk required"
        ),
        CategoryAllocation(
            name="Protein",
            priority=3,
            estimated_budget=20.0,
            target_quantity="high",
            reasoning="High protein diet requested"
        )
    ],
    total_budget=43.0,
    goal_confidence=0.98,
    planning_confidence=0.95,
    assumptions=["Assumed basic protein sources"]
)

def run_evaluations():
    print("Starting retrieval evaluation...")
    db = SessionLocal()
    try:
        service = RetrievalService(db)
        
        result, metadata = service.retrieve_products(TEST_PLAN)
        
        print("\n=== RETRIEVAL RESULTS ===")
        print(f"Total Candidates Found: {result.total_candidates}")
        print(f"Latency: {metadata['latency_sec']:.2f}s")
        
        for cat_result in result.categories:
            print(f"\nCategory Slice: {cat_result.category_name} (Budget: ${cat_result.requested_budget:.2f})")
            if not cat_result.candidates:
                print("  [WARNING] No candidates found!")
                continue
                
            for cand in cat_result.candidates:
                print(f"  - {cand.product_name} (${cand.price:.2f})")
                print(f"    Similarity: {cand.similarity_score} | Method: {cand.retrieval_method}")
                
    except Exception as e:
        print(f"ERROR: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    run_evaluations()
