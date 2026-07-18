from pydantic import BaseModel
from typing import Optional
from app.ai.retrieval.models import RetrievalResult
from app.ai.verification.models import VerificationResult

class VerificationRequest(BaseModel):
    retrieval_result: RetrievalResult

class VerificationResponse(BaseModel):
    success: bool
    data: Optional[VerificationResult] = None
    metadata: Optional[dict] = None
