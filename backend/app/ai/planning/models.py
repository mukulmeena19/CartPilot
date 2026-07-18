from pydantic import BaseModel, Field
from typing import List, Optional

# --- AI INFERENCE MODELS ---
class InferredCategory(BaseModel):
    name: str = Field(..., description="The abstract category name (e.g. 'Protein', 'Produce')")
    weight: float = Field(..., description="Relative semantic weight (1.0 to 10.0)")
    target_quantity: str = Field(..., description="Estimated abstract volume: 'low', 'medium', 'high'")
    reasoning: str = Field(..., description="Brief explanation of why this category was selected")

class AIPlanningInference(BaseModel):
    """What the LLM outputs before Rules apply"""
    categories: List[InferredCategory]
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")

# --- FINAL DOMAIN MODELS ---
class CategoryAllocation(BaseModel):
    name: str
    priority: int
    estimated_budget: float
    target_quantity: str
    reasoning: str

class ShoppingPlan(BaseModel):
    categories: List[CategoryAllocation]
    total_budget: float
    goal_confidence: float
    planning_confidence: float
    assumptions: List[str] = Field(default_factory=list)
