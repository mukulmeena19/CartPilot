import asyncio
import uuid
import datetime
from typing import AsyncGenerator, Any
import structlog
import json

from app.schemas.conversation import StreamEvent

logger = structlog.get_logger(__name__)

class ConversationManager:
    def __init__(self):
        # We would inject dependencies here like goal_service, retrieval_service, etc.
        pass
        
    def _create_event(self, event_type: str, data: dict) -> StreamEvent:
        return StreamEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.datetime.utcnow().isoformat() + "Z",
            event=event_type,
            data=data
        )

    async def process_conversation(self, query: str) -> AsyncGenerator[StreamEvent, None]:
        """
        Orchestrates the conversational flow and yields domain events.
        """
        try:
            # 0. Prompt Security Scan
            from app.core.security import PromptSecurity
            is_safe, reason = PromptSecurity.scan_input(query)
            if not is_safe:
                yield self._create_event("error", {
                    "code": "SECURITY_VIOLATION",
                    "message": "I cannot fulfill this request as it violates safety policies."
                })
                return

            # 1. Connected
            yield self._create_event("connected", {"status": "ok"})
            
            # Simulate slight network delay
            await asyncio.sleep(0.5)

            # 2. Thinking
            yield self._create_event("thinking", {"step": "Understanding request"})
            await asyncio.sleep(1.0)
            
            # 3. Intent
            yield self._create_event("intent", {"intent": "shopping", "confidence": 0.95})
            
            # 4. Workflow
            yield self._create_event("workflow", {"workflow_type": "grocery"})
            
            # 5. Retrieval
            yield self._create_event("thinking", {"step": "Searching for high protein options"})
            await asyncio.sleep(1.0)
            yield self._create_event("retrieval", {"candidate_count": 42})
            
            # 6. Ranking
            yield self._create_event("thinking", {"step": "Ranking products based on preferences"})
            await asyncio.sleep(1.0)
            yield self._create_event("ranking", {"top_k": 5})
            
            # 7. Recommendations
            recommendations = [
                {
                    "id": "prod_1",
                    "type": "product",
                    "title": "Amul High Protein Lassi",
                    "brand": "Amul",
                    "price": 40.0,
                    "match_score": 95,
                    "protein": "15g",
                    "image_url": None,
                    "reasons": ["Meets high protein criteria", "Fits vegetarian diet"]
                },
                {
                    "id": "prod_2",
                    "type": "product",
                    "title": "Whole Truth Protein Bars",
                    "brand": "The Whole Truth",
                    "price": 450.0,
                    "match_score": 88,
                    "protein": "20g",
                    "image_url": None,
                    "reasons": ["Excellent macro ratio", "No added sugar"]
                }
            ]
            yield self._create_event("recommendations", {"items": recommendations})
            
            # 8. Assistant Chunks
            response_text = "I've found some excellent high-protein options for you. The Amul Lassi is a great quick drink, and The Whole Truth bars are perfect for on-the-go snacking. Would you like me to add these to your cart?"
            
            # Simulate streaming words
            words = response_text.split(" ")
            for i in range(0, len(words), 3):
                chunk = " ".join(words[i:i+3]) + " "
                yield self._create_event("assistant_chunk", {"text": chunk})
                await asyncio.sleep(0.2)
                
            # 9. Done
            yield self._create_event("done", {})
            
        except asyncio.CancelledError:
            logger.warning("Conversation processing was cancelled.")
            raise
        except Exception as e:
            logger.error("Error in conversation processing", error=str(e))
            yield self._create_event("error", {
                "code": "PROCESSING_ERROR",
                "message": "An error occurred while processing your request."
            })
