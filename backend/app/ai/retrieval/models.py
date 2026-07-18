from pydantic import BaseModel, Field
from typing import List, Optional

class ProductCandidate(BaseModel):
    product_id: int
    product_name: str
    category_name: str
    price: float
    similarity_score: float
    retrieval_method: str = "hybrid"
    matched_attributes: List[str] = Field(default_factory=list)
    embedding_model: str

class CategoryRetrievalResult(BaseModel):
    category_name: str
    requested_budget: float
    candidates: List[ProductCandidate]

class RetrievalResult(BaseModel):
    categories: List[CategoryRetrievalResult]
    total_candidates: int
