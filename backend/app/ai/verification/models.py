from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.ai.retrieval.models import ProductCandidate

class VerifiedCandidate(BaseModel):
    """
    The fully verified result for a single candidate product.
    Contains detailed explainability for optimization decisions.
    """
    candidate: ProductCandidate
    verification_status: bool = Field(..., description="True if purchasable, False otherwise")
    verification_reason: str = Field(..., description="Reason for rejection, or 'Valid'")
    stock_available: bool = Field(..., description="True if stock > 0")
    available_quantity: int = Field(0, description="Exact number of items in stock")
    price_verified: bool = Field(..., description="True if price is valid (>0 and sane)")
    merchant_available: bool = Field(True, description="True if merchant is currently accepting orders")
    verification_timestamp: datetime = Field(..., description="When the verification occurred")
    verification_score: float = Field(..., description="Heuristic score 0.0 to 1.0 for future optimization")
    
class CategoryVerificationResult(BaseModel):
    category_name: str
    verified_candidates: List[VerifiedCandidate]

class VerificationResult(BaseModel):
    categories: List[CategoryVerificationResult]
    total_verified: int
    total_rejected: int
