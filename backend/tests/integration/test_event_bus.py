import pytest
import asyncio
from app.events.bus import EventBus, Event, EventType

@pytest.mark.asyncio
async def test_event_bus_pub_sub():
    bus = EventBus()
    received_events = []

    async def mock_subscriber(event: Event):
        received_events.append(event)

    bus.subscribe(EventType.CONVERSATION_STARTED, mock_subscriber)
    
    event = Event(
        event_type=EventType.CONVERSATION_STARTED,
        user_id=1,
        session_id="session-123"
    )
    
    await bus.emit(event)
    # Give the async task a moment to run
    await asyncio.sleep(0.01)
    
    assert len(received_events) == 1
    assert received_events[0].session_id == "session-123"

@pytest.mark.asyncio
async def test_event_bus_exception_isolation():
    bus = EventBus()
    received_events = []

    async def failing_subscriber(event: Event):
        raise ValueError("Subscriber failed")

    async def successful_subscriber(event: Event):
        received_events.append(event)

    bus.subscribe(EventType.WORKFLOW_COMPLETED, failing_subscriber)
    bus.subscribe(EventType.WORKFLOW_COMPLETED, successful_subscriber)
    
    event = Event(event_type=EventType.WORKFLOW_COMPLETED, session_id="test")
    
    await bus.emit(event)
    await asyncio.sleep(0.01)
    
    # Successful subscriber should still receive the event despite the failure in the other
    assert len(received_events) == 1
    assert received_events[0].session_id == "test"
