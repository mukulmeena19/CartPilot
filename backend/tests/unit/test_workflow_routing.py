import pytest
from unittest.mock import MagicMock
from app.services.conversation_manager import ConversationManager
from app.ai.goal_understanding.models import GoalContext

@pytest.mark.asyncio
async def test_workflow_routing_ambiguous(db_session):
    """
    Tests that an ambiguous query (e.g. 'cheap dinner ideas') defaults to the grocery workflow
    when it does not explicitly mention 'food' or 'restaurant' in the generated goal_type.
    """
    manager = ConversationManager(db_session)
    
    # Mock Goal Understanding to return a generic/ambiguous goal type
    manager.understanding.understand_goal = MagicMock(return_value=(
        GoalContext(
            goal_type="meal_ideas", # Ambiguous, doesn't contain 'food' or 'restaurant'
            shopping_goal="cheap dinner ideas",
            confidence=0.7
        ),
        {}
    ))
    
    # We mock execute_workflow to avoid actually running the pipeline
    manager.registry.execute_workflow = MagicMock()
    
    events = []
    async for event in manager.process_conversation("cheap dinner ideas", user_id=1):
        events.append(event)
        
    # Check that it routed to grocery
    workflow_events = [e for e in events if e.event == "workflow"]
    assert len(workflow_events) > 0
    assert workflow_events[0].data["workflow_type"] == "grocery"
