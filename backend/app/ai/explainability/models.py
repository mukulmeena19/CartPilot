from pydantic import BaseModel, Field
from typing import List, Optional
from app.ai.optimization.models import OptimizedCandidate, OptimizedShoppingPlan

class ProductExplanation(BaseModel):
    product_id: int
    product_name: str
    explanation_text: str = Field(..., description="The human readable explanation")
    supporting_rules: List[str] = Field(default_factory=list, description="List of internal rule codes triggered")
    optimization_score: float
    verification_status: bool
    budget_fit: bool
    preference_applied: bool

class ExplainableCategory(BaseModel):
    category_name: str
    selected_items: List[ProductExplanation]
    total_cost: float

class ExplainableShoppingPlan(BaseModel):
    categories: List[ExplainableCategory]
    total_budget_used: float
    total_budget_allocated: float
    optimization_success_rate: float
    summary: Optional[str] = None
