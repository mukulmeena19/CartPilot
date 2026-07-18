from pydantic import BaseModel, Field
from typing import List, Optional

class GoalContext(BaseModel):
    """
    Internal domain model representing the LLM's parsed understanding of a shopping goal.
    This model defines the exact JSON schema the LLM is forced to output.
    """
    goal_type: str = Field(..., description="The type of goal (e.g., meal_prep, weekly_groceries, event)")
    shopping_goal: str = Field(..., description="Concise 3-5 word summary of the objective")
    people: Optional[int] = Field(None, description="Number of people being shopped for, if mentioned")
    budget: Optional[float] = Field(None, description="The maximum budget in the local currency, if mentioned")
    duration: Optional[str] = Field(None, description="The timeframe (e.g., '1 week', '3 days'), if mentioned")
    dietary_preferences: List[str] = Field(default_factory=list, description="Explicit dietary needs (e.g., vegan, halal)")
    brand_preferences: List[str] = Field(default_factory=list, description="Explicit brand requests")
    constraints: List[str] = Field(default_factory=list, description="Other hard rules (e.g., organic only)")
    confidence: float = Field(..., description="Float from 0.0 to 1.0 indicating clarity of understanding")
