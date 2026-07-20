from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
import json
import asyncio
import structlog
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.conversation import ConversationRequest
from app.services.conversation_manager import ConversationManager

logger = structlog.get_logger(__name__)
router = APIRouter()

async def sse_event_generator(request: Request, manager: ConversationManager, query: str):
    """
    Generator that consumes domain events from the ConversationManager and yields them as SSE strings.
    """
    try:
        # We use a hardcoded user_id=1 for now as frontend doesn't pass auth token
        async for event in manager.process_conversation(query, user_id=1):
            # If client disconnected, stop generating
            if await request.is_disconnected():
                logger.info("Client disconnected from SSE stream.")
                break
                
            # Serialize event data
            event_data_json = json.dumps(event.data)
            
            # SSE format: event: [name]\ndata: [json]\n\n
            sse_message = f"id: {event.id}\nevent: {event.event}\ndata: {event_data_json}\n\n"
            yield sse_message
            
            if event.event == "done" or event.event == "error":
                break
                
    except asyncio.CancelledError:
        logger.warning("SSE generation was cancelled.")
        raise
    except Exception as e:
        logger.error("Error generating SSE events", error=str(e))
        error_msg = json.dumps({"code": "INTERNAL_ERROR", "message": "Stream generation failed."})
        yield f"event: error\ndata: {error_msg}\n\n"


@router.post("/stream")
async def stream_conversation(
    req_data: ConversationRequest, 
    request: Request,
    db: Session = Depends(deps.get_db)
):
    """
    Endpoint for streaming conversation events via SSE.
    """
    manager = ConversationManager(db)
    
    return StreamingResponse(
        sse_event_generator(request, manager, req_data.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
