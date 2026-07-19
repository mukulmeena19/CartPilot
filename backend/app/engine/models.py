from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class PluginResult(BaseModel):
    score: float
    reason: Optional[str] = None
    weight: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CandidateScore(BaseModel):
    candidate_id: str
    item: Any = Field(exclude=True) # Exclude from serialized output
    
    semantic_score: float = 0.0
    fts_score: float = 0.0
    
    # Plugin specific scores
    nutrition_score: float = 0.0
    budget_score: float = 0.0
    personalization_score: float = 0.0
    popularity_score: float = 0.0
    
    plugin_results: Dict[str, PluginResult] = Field(default_factory=dict)
    
    final_score: float = 0.0
    reasons: List[str] = Field(default_factory=list)
    
    # Enriched metadata (pricing, tags, etc. to be used by plugins)
    enriched_data: Dict[str, Any] = Field(default_factory=dict)

class RecommendationResponse(BaseModel):
    id: str
    name: str
    price: float
    image_url: Optional[str] = None
    reasons: List[str] = Field(default_factory=list)
    final_score: float
