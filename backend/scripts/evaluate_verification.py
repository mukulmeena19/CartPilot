import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.ai.retrieval.models import RetrievalResult, CategoryRetrievalResult, ProductCandidate
from app.ai.verification.service import VerificationService

# Create a mock Retrieval Result covering various edge cases
TEST_RETRIEVAL = RetrievalResult(
    categories=[
        CategoryRetrievalResult(
            category_name="Produce",
            requested_budget=15.0,
            candidates=[
                ProductCandidate(
                    product_id=1, # Assume valid and in stock
                    product_name="Organic Bananas",
                    category_name="Produce",
                    price=2.50,
                    similarity_score=0.98,
                    embedding_model="test"
                ),
                ProductCandidate(
                    product_id=9999, # Invalid / Doesn't exist -> should fail inventory/activity
                    product_name="Ghost Product",
                    category_name="Produce",
                    price=1.00,
                    similarity_score=0.95,
                    embedding_model="test"
                )
            ]
        ),
        CategoryRetrievalResult(
            category_name="Dairy",
            requested_budget=10.0,
            candidates=[
                ProductCandidate(
                    product_id=2, 
                    product_name="Whole Milk",
                    category_name="Dairy",
                    price=-5.00, # Invalid price!
                    similarity_score=0.90,
                    embedding_model="test"
                ),
                ProductCandidate(
                    product_id=1, # DUPLICATE from produce! Should be filtered out
                    product_name="Organic Bananas",
                    category_name="Produce",
                    price=2.50,
                    similarity_score=0.88,
                    embedding_model="test"
                )
            ]
        )
    ],
    total_candidates=4
)

def run_evaluations():
    print("Starting verification evaluation...")
    db = SessionLocal()
    try:
        service = VerificationService(db)
        
        result, metadata = service.verify(TEST_RETRIEVAL)
        
        print("\n=== VERIFICATION RESULTS ===")
        print(f"Total Verified (Pass): {result.total_verified}")
        print(f"Total Rejected (Fail): {result.total_rejected}")
        print(f"Latency: {metadata['latency_sec']:.4f}s")
        
        for cat_result in result.categories:
            print(f"\nCategory: {cat_result.category_name}")
            for vc in cat_result.verified_candidates:
                status = "PASS" if vc.verification_status else "FAIL"
                print(f"  [{status}] {vc.candidate.product_name} (ID: {vc.candidate.product_id})")
                print(f"    Reason: {vc.verification_reason}")
                print(f"    Score:  {vc.verification_score}")
                print(f"    Stock:  {vc.available_quantity}")
                
    except Exception as e:
        print(f"ERROR: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    run_evaluations()
