from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api import deps
from app.db.models.user import User
from app.ai.orchestrator import PipelineOrchestrator
import structlog

logger = structlog.get_logger(__name__)
router = APIRouter()
orchestrator = PipelineOrchestrator()

class GenerateCartRequest(BaseModel):
    query: str

@router.post("/generate-cart")
async def generate_cart(
    request: GenerateCartRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Streams the AI Shopping Pipeline progress via Server-Sent Events (SSE).
    """
    return StreamingResponse(
        orchestrator.generate_cart_stream(request.query, current_user, db),
        media_type="text/event-stream"
    )
