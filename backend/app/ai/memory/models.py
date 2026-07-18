from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime, timezone

class PreferenceSignal(BaseModel):
    value: str = Field(..., description="The actual preference (e.g. 'Amul', 'Vegan')")
    confidence: float = Field(..., ge=0.0, le=1.0, description="0.0 to 1.0 confidence score")
    source: str = Field(..., description="'explicit' or 'inferred'")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserPreferenceContext(BaseModel):
    """
    The unified Pydantic schema representing the JSONB payload in the DB.
    Also used as the output for the Optimizer to consume.
    """
    brands: Dict[str, PreferenceSignal] = Field(default_factory=dict)
    categories: Dict[str, PreferenceSignal] = Field(default_factory=dict)
    dietary: Dict[str, PreferenceSignal] = Field(default_factory=dict)
    allergies: Dict[str, PreferenceSignal] = Field(default_factory=dict)
    price_sensitivity: str = Field("medium", description="'low', 'medium', 'high'")
    merchant_preferences: Dict[str, PreferenceSignal] = Field(default_factory=dict)
    
    # Track historical outliers or hard rejections
    rejected_products: List[int] = Field(default_factory=list, description="List of product IDs explicitly rejected")
