from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from app.ai.verification.models import VerifiedCandidate
from app.ai.planning.models import CategoryAllocation

class OptimizationTrace(BaseModel):
    """Internal trace for future explainability"""
    product_id: int
    product_name: str
    original_score: float = 0.0
    final_score: float = 0.0
    dropped: bool = False
    drop_reason: Optional[str] = None
    bonuses_applied: List[str] = Field(default_factory=list)
    penalties_applied: List[str] = Field(default_factory=list)

class OptimizedCandidate(BaseModel):
    candidate: VerifiedCandidate
    final_score: float
    optimization_trace: OptimizationTrace

class OptimizedCategory(BaseModel):
    allocation: CategoryAllocation
    selected_items: List[OptimizedCandidate]
    total_cost: float

class OptimizedShoppingPlan(BaseModel):
    categories: List[OptimizedCategory]
    total_budget_used: float
    total_budget_allocated: float
    optimization_success_rate: float # % of categories fulfilled
