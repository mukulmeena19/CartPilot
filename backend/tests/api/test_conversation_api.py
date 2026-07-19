import pytest
from fastapi import FastAPI, APIRouter
from fastapi.testclient import TestClient

# Mock a simple router for testing the API contract of the conversation engine
app = FastAPI()
router = APIRouter()

@router.post("/api/v1/conversation/{session_id}/message")
def post_message(session_id: str, message: dict):
    if not message.get("content"):
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Message content required")
        
    return {
        "success": True,
        "type": "workflow_result",
        "message": "Processed message",
        "results": {}
    }

app.include_router(router)

client = TestClient(app)

def test_conversation_api_contract():
    response = client.post("/api/v1/conversation/session-123/message", json={"content": "I want to order food."})
    
    # Verify HTTP status codes
    assert response.status_code == 200
    
    # Verify response schema
    data = response.json()
    assert "success" in data
    assert "type" in data
    assert "message" in data
    assert data["type"] == "workflow_result"

def test_conversation_api_validation():
    # Test missing content
    response = client.post("/api/v1/conversation/session-123/message", json={})
    
    # Verify validation errors are handled
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
