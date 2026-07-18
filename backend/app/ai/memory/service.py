import time
import structlog
from typing import Tuple, Dict, Any
from sqlalchemy.orm import Session
from app.ai.memory.models import UserPreferenceContext
from app.ai.memory.schemas import UpdatePreferenceRequest
from app.ai.memory.preference_store import PreferenceStore
from app.ai.memory.preference_extractor import PreferenceExtractor

logger = structlog.get_logger(__name__)

class MemoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_preferences(self, user_id: int) -> Tuple[UserPreferenceContext, Dict[str, Any]]:
        start_time = time.time()
        logger.info("Fetching user preferences", user_id=user_id)
        
        try:
            context = PreferenceStore.get_preferences(self.db, user_id)
            latency = time.time() - start_time
            return context, {"latency_sec": latency}
        except Exception as e:
            logger.error("Failed to fetch preferences", user_id=user_id, error=str(e))
            raise

    def update_preference(
        self, user_id: int, request: UpdatePreferenceRequest
    ) -> Tuple[UserPreferenceContext, Dict[str, Any]]:
        start_time = time.time()
        logger.info(
            "Updating user preference", 
            user_id=user_id, 
            type=request.preference_type, 
            value=request.value,
            action=request.action
        )
        
        try:
            # 1. Load existing
            context = PreferenceStore.get_preferences(self.db, user_id)
            
            # 2. Apply mathematical decay/growth
            updated_context = PreferenceExtractor.apply_signal(
                context=context,
                preference_type=request.preference_type,
                value=request.value,
                action=request.action,
                source=request.source
            )
            
            # 3. Save back to DB
            PreferenceStore.save_preferences(self.db, user_id, updated_context)
            
            latency = time.time() - start_time
            logger.info("Successfully updated preference", user_id=user_id, latency_sec=latency)
            
            return updated_context, {"latency_sec": latency}
        except Exception as e:
            logger.error("Failed to update preference", user_id=user_id, error=str(e))
            raise
