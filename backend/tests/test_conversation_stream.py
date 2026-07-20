import pytest
import asyncio
import json
from unittest.mock import MagicMock, patch

from app.schemas.conversation import StreamEvent
from app.services.conversation_manager import ConversationManager
from app.ai.goal_understanding.models import GoalContext
from app.db.models.user import User

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.mark.asyncio
async def test_grocery_workflow_stream(mock_db):
    """
    Tests that the conversation manager yields the expected sequence of SSE events
    for a grocery intent, simulating the 8-stage UI.
    """
    manager = ConversationManager(mock_db)
    
    # Mock Goal Understanding to return 'grocery'
    manager.understanding.understand_goal = MagicMock(return_value=(
        GoalContext(
            goal_type="meal_prep",
            shopping_goal="high protein snacks",
            confidence=0.9
        ),
        {}
    ))
    
    # Execute stream
    events = []
    async for event in manager.process_conversation("I need high protein snacks", user_id=1):
        events.append(event)
        
    event_names = [e.event for e in events]
    
    # Assert sequence matches the 8 stages
    assert "understanding" in event_names
    assert "planning" in event_names
    assert "searching" in event_names
    assert "verifying" in event_names
    assert "applying" in event_names
    assert "optimizing" in event_names
    assert "finalizing" in event_names
    assert "complete" in event_names
    
    # Assert correct order
    expected_sequence = [
        "understanding", "planning", "searching", "verifying",
        "applying", "optimizing", "finalizing", "complete"
    ]
    actual_sequence = [e for e in event_names if e in expected_sequence]
    assert actual_sequence == expected_sequence
    
    # Assert the workflow was set correctly
    workflow_events = [e for e in events if e.event == "workflow"]
    assert len(workflow_events) > 0
    assert workflow_events[0].data["workflow_type"] == "grocery"

@pytest.mark.asyncio
async def test_food_workflow_stream(mock_db):
    """
    Tests that the conversation manager routes to the food workflow and goes through the 8 stages.
    """
    manager = ConversationManager(mock_db)
    
    goal_context = GoalContext(
        goal_type="food_order",
        shopping_goal="order pizza",
        confidence=0.9
    )
    
    manager.understanding.understand_goal = MagicMock(return_value=(
        goal_context,
        {}
    ))
    
    events = []
    async for event in manager.process_conversation("Order me pizza", user_id=1):
        events.append(event)
        
    event_names = [e.event for e in events]
    
    assert "understanding" in event_names
    assert "planning" in event_names
    assert "searching" in event_names
    assert "verifying" in event_names
    assert "applying" in event_names
    assert "optimizing" in event_names
    assert "finalizing" in event_names
    assert "complete" in event_names
    
    workflow_events = [e for e in events if e.event == "workflow"]
    assert workflow_events[0].data["workflow_type"] == "food"
    
    # Due to mock_db returning empty, it falls back
    rec_events = [e for e in events if e.event == "complete"]
    assert len(rec_events) > 0
    assert rec_events[0].data["items"] == []
    
    # Assert fallback message was sent in explanation
    assert "restaurant options" in rec_events[0].data["cart"]["explanation"]["summary"]
