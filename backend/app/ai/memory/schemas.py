from pydantic import BaseModel
from typing import Optional
from app.ai.memory.models import UserPreferenceContext

class UpdatePreferenceRequest(BaseModel):
    preference_type: str # 'brands', 'dietary', 'allergies'
    value: str
    action: str # 'positive' (like/buy) or 'negative' (dislike/reject)
    source: str = "explicit"

class MemoryResponse(BaseModel):
    success: bool
    data: Optional[UserPreferenceContext] = None
    metadata: Optional[dict] = None
