import sys
import os
import asyncio
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.user import User
from app.ai.orchestrator import PipelineOrchestrator
import uuid

async def test_pipeline():
    print("Starting E2E Pipeline Test...")
    
    # 1. Force Mock Provider
    os.environ["LLM_PROVIDER"] = "mock"
    
    db: Session = SessionLocal()
    try:
        # Create a mock user
        user = User(
            id=str(uuid.uuid4()), 
            email="test@cartpilot.com", 
            hashed_password="mock",
            preferences={"preferred_brands": ["Amul"], "dietary": ["vegetarian"]}
        )
        
        orchestrator = PipelineOrchestrator()
        
        query = "I need groceries for a week of high-protein vegetarian meals under 2500."
        print(f"Testing Query: {query}")
        
        start_time = time.time()
        
        # 2. Consume the generator
        stages_emitted = []
        async for sse_event in orchestrator.generate_cart_stream(query, user, db):
            print(f"Received SSE: {sse_event.strip()}")
            if '"stage": "' in sse_event:
                stage = sse_event.split('"stage": "')[1].split('"')[0]
                stages_emitted.append(stage)
        
        total_time = time.time() - start_time
        
        # 3. Validation
        expected_stages = [
            "UNDERSTANDING", "PLANNING", "RETRIEVAL", 
            "VERIFICATION", "MEMORY", "OPTIMIZATION", 
            "EXPLAINABILITY", "COMPLETE"
        ]
        
        for expected in expected_stages:
            if expected not in stages_emitted:
                print(f"❌ FAILED: Missing stage {expected}")
                sys.exit(1)
                
        if "ERROR" in stages_emitted:
            print("❌ FAILED: Pipeline emitted an ERROR stage")
            sys.exit(1)
            
        print("\n" + "="*40)
        print("PERFORMANCE REPORT")
        print("="*40)
        print(f"Total Execution Time: {total_time:.3f} seconds")
        print("Pipeline Status: HEALTHY")
        print("="*40 + "\n")
        
        print("✅ E2E Pipeline Test Passed Successfully!")
        
    except Exception as e:
        print(f"❌ FAILED with exception: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_pipeline())
