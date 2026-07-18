from pydantic import BaseModel
from typing import List, Optional

class GoalUnderstandingRequest(BaseModel):
    query: str

class GoalUnderstandingResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    metadata: Optional[dict] = None
