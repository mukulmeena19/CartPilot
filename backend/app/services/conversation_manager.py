import asyncio
import uuid
import datetime
from typing import AsyncGenerator, Any
import structlog
import json
from sqlalchemy.orm import Session

from app.schemas.conversation import StreamEvent
from app.core.security import PromptSecurity
from app.ai.goal_understanding.service import GoalUnderstandingService
from app.workflows.registry import WorkflowRegistry
from app.workflows.context import WorkflowContext

logger = structlog.get_logger(__name__)

class ConversationManager:
    def __init__(self, db: Session):
        self.db = db
        self.understanding = GoalUnderstandingService()
        self.registry = WorkflowRegistry(db)
        
    def _create_event(self, event_type: str, data: dict) -> StreamEvent:
        return StreamEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.datetime.utcnow().isoformat() + "Z",
            event=event_type,
            data=data
        )

    async def process_conversation(self, query: str, user_id: int, session_id: str = None) -> AsyncGenerator[StreamEvent, None]:
        """
        Orchestrates the conversational flow and yields domain events.
        """
        if not session_id:
            session_id = str(uuid.uuid4())
            
        queue = asyncio.Queue()
        
        async def emit(event_type: str, data: dict = None):
            await queue.put(self._create_event(event_type, data or {}))
            
        async def run_workflow():
            try:
                # 0. Prompt Security Scan
                is_safe, reason = PromptSecurity.scan_input(query)
                if not is_safe:
                    await emit("error", {
                        "code": "SECURITY_VIOLATION",
                        "message": "I cannot fulfill this request as it violates safety policies."
                    })
                    return

                # 1. Connected
                await emit("connected", {"status": "ok"})
                
                # 2. Understanding
                await emit("understanding", {"step": "Analyzing your request..."})
                goal_context, _ = self.understanding.understand_goal(query)
                
                # Infer domain from goal_type
                if "food" in goal_context.goal_type or "restaurant" in goal_context.goal_type or "restaurant" in query.lower() or "near me" in query.lower() or "biryani" in query.lower():
                    domain = "food"
                else:
                    domain = "grocery"
                
                # 3. Intent & Workflow
                await emit("intent", {"intent": domain, "confidence": 0.95})
                await emit("workflow", {"workflow_type": domain})
                
                # 4. Execute Workflow
                context = WorkflowContext(
                    session_id=session_id,
                    user_id=user_id,
                    intent=domain,
                    extracted_entities=goal_context.model_dump(),
                    emit_cb=emit
                )
                
                await self.registry.execute_workflow(context)
                
            except Exception as e:
                logger.error("Error in conversation processing", error=str(e), exc_info=True)
                await emit("error", {
                    "code": "PROCESSING_ERROR",
                    "message": "An error occurred while processing your request."
                })
            finally:
                # Sentinel to end the generator
                await queue.put(None)

        # Run the workflow in the background
        task = asyncio.create_task(run_workflow())
        
        # Yield from the queue
        try:
            while True:
                event = await queue.get()
                if event is None:
                    break
                yield event
        except asyncio.CancelledError:
            logger.warning("Conversation processing was cancelled.")
            task.cancel()
            raise
