import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models.user import User
from app.ai.memory.service import MemoryService
from app.ai.memory.schemas import UpdatePreferenceRequest

def run_evaluations():
    print("Starting memory evaluation...")
    db = SessionLocal()
    
    # Setup test user
    test_email = f"memory_test_{int(datetime.now().timestamp())}@example.com"
    test_user = User(
        email=test_email,
        hashed_password="hashed",
        full_name="Memory Tester",
        preferences={} # Empty start
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    user_id = test_user.id
    print(f"Created test user ID: {user_id}")
    
    try:
        service = MemoryService(db)
        
        # 1. Empty fetch
        ctx, _ = service.get_user_preferences(user_id)
        print("\n1. Initial state:")
        print(ctx.model_dump())
        
        # 2. Add an explicit brand preference
        print("\n2. Applying Positive Explicit Signal (Amul)")
        req1 = UpdatePreferenceRequest(
            preference_type="brands",
            value="Amul",
            action="positive",
            source="explicit"
        )
        ctx, _ = service.update_preference(user_id, req1)
        print(f"Confidence: {ctx.brands['Amul'].confidence}") # Should be 1.0
        
        # 3. Simulate an inferred rejection of the same brand
        print("\n3. Applying Negative Inferred Signal (Decay)")
        req2 = UpdatePreferenceRequest(
            preference_type="brands",
            value="Amul",
            action="negative",
            source="inferred"
        )
        ctx, _ = service.update_preference(user_id, req2)
        print(f"Confidence after decay: {ctx.brands['Amul'].confidence}") # Should be 0.95 (explicit resists inferred decay)
        
        # 4. Add dietary preference
        print("\n4. Applying Dietary Preference")
        req3 = UpdatePreferenceRequest(
            preference_type="dietary",
            value="Vegan",
            action="positive",
            source="explicit"
        )
        ctx, _ = service.update_preference(user_id, req3)
        print(f"Dietary: {list(ctx.dietary.keys())}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
    finally:
        # Cleanup
        db.delete(test_user)
        db.commit()
        db.close()
        print("\nCleanup complete.")

if __name__ == "__main__":
    run_evaluations()
