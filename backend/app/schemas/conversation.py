from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Literal

class BaseRecommendation(BaseModel):
    id: str
    type: Literal["product", "recipe", "restaurant"]
    title: str
    reasons: List[str]

class ProductRecommendation(BaseRecommendation):
    type: Literal["product"] = "product"
    brand: Optional[str] = None
    price: float
    match_score: int
    protein: Optional[str] = None
    image_url: Optional[str] = None

class RecipeRecommendation(BaseRecommendation):
    type: Literal["recipe"] = "recipe"
    rating: float
    time_mins: int
    estimated_price: float
    protein: str
    image_url: Optional[str] = None

class RestaurantRecommendation(BaseRecommendation):
    type: Literal["restaurant"] = "restaurant"
    rating: float
    delivery_time_mins: int
    estimated_price: float

class StreamEvent(BaseModel):
    id: str
    timestamp: str
    event: Literal[
        "connected", 
        "understanding",
        "intent", 
        "workflow", 
        "planning",
        "searching",
        "verifying",
        "applying",
        "optimizing",
        "finalizing",
        "complete",
        "error"
    ]
    data: Dict[str, Any]

class ConversationRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
