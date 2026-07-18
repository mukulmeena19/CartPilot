from pydantic import BaseModel
from typing import Optional
from app.ai.planning.models import ShoppingPlan
from app.ai.retrieval.models import RetrievalResult

class RetrievalRequest(BaseModel):
    shopping_plan: ShoppingPlan

class RetrievalResponse(BaseModel):
    success: bool
    data: Optional[RetrievalResult] = None
    metadata: Optional[dict] = None
