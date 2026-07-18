from pydantic import BaseModel
from typing import Optional, List
from app.ai.planning.models import ShoppingPlan
from app.ai.verification.models import VerificationResult
from app.ai.memory.models import UserPreferenceContext
from app.ai.optimization.models import OptimizedShoppingPlan

class OptimizationRequest(BaseModel):
    shopping_plan: ShoppingPlan
    verification_result: VerificationResult
    user_preferences: Optional[UserPreferenceContext] = None

class OptimizationResponse(BaseModel):
    success: bool
    data: Optional[OptimizedShoppingPlan] = None
    metadata: Optional[dict] = None
