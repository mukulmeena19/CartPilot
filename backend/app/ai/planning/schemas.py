from pydantic import BaseModel
from typing import List, Optional
from app.ai.goal_understanding.models import GoalContext
from app.ai.planning.models import ShoppingPlan

class PlanningRequest(BaseModel):
    goal_context: GoalContext

class PlanningResponse(BaseModel):
    success: bool
    data: Optional[ShoppingPlan] = None
    metadata: Optional[dict] = None
