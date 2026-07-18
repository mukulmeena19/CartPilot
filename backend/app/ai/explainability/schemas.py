from pydantic import BaseModel
from typing import Optional
from app.ai.optimization.models import OptimizedShoppingPlan
from app.ai.explainability.models import ExplainableShoppingPlan

class ExplainPlanRequest(BaseModel):
    optimized_plan: OptimizedShoppingPlan

class ExplainPlanResponse(BaseModel):
    success: bool
    data: Optional[ExplainableShoppingPlan] = None
    metadata: Optional[dict] = None
