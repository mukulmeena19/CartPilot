from fastapi import APIRouter, HTTPException, Depends
from typing import Any
from app.api import deps
from app.ai.goal_understanding.schemas import GoalUnderstandingRequest, GoalUnderstandingResponse
from app.ai.goal_understanding.service import GoalUnderstandingService
from app.ai.planning.schemas import PlanningRequest, PlanningResponse
from app.ai.planning.service import PlanningService
from app.ai.retrieval.schemas import RetrievalRequest, RetrievalResponse
from app.ai.retrieval.service import RetrievalService
from app.ai.verification.schemas import VerificationRequest, VerificationResponse
from app.ai.verification.service import VerificationService
from app.ai.explainability.schemas import ExplainPlanRequest, ExplainPlanResponse
from app.ai.explainability.service import ExplainabilityService
from app.ai.exceptions import GoalUnderstandingError
import structlog
from app.db.session import get_db

logger = structlog.get_logger(__name__)
router = APIRouter()
goal_service = GoalUnderstandingService()
planning_service = PlanningService()
explainability_service = ExplainabilityService()

@router.post("/understand-goal", response_model=GoalUnderstandingResponse)
def understand_goal(
    request: GoalUnderstandingRequest,
    current_user = Depends(deps.get_current_user)
) -> Any:
    try:
        goal_context, metadata = goal_service.understand_goal(request.query)
        
        return GoalUnderstandingResponse(
            success=True,
            data=goal_context.model_dump(),
            metadata=metadata
        )
    except GoalUnderstandingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("AI service encountered a critical error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/plan-goal", response_model=PlanningResponse)
def plan_goal(
    request: PlanningRequest,
    current_user = Depends(deps.get_current_user)
) -> Any:
    try:
        plan, metadata = planning_service.plan_goal(request.goal_context)
        
        return PlanningResponse(
            success=True,
            data=plan,
            metadata=metadata
        )
    except Exception as e:
        logger.error("Planning service encountered a critical error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/retrieve-products", response_model=RetrievalResponse)
def retrieve_products(
    request: RetrievalRequest,
    current_user = Depends(deps.get_current_user),
    db = Depends(get_db)
) -> Any:
    try:
        retrieval_service = RetrievalService(db)
        result, metadata = retrieval_service.retrieve_products(request.shopping_plan)
        
        return RetrievalResponse(
            success=True,
            data=result,
            metadata=metadata
        )
    except Exception as e:
        logger.error("Retrieval service encountered a critical error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/verify-candidates", response_model=VerificationResponse)
def verify_candidates(
    request: VerificationRequest,
    current_user = Depends(deps.get_current_user),
    db = Depends(get_db)
) -> Any:
    try:
        verification_service = VerificationService(db)
        result, metadata = verification_service.verify(request.retrieval_result)
        
        return VerificationResponse(
            success=True,
            data=result,
            metadata=metadata
        )
    except Exception as e:
        logger.error("Verification service encountered a critical error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/explain-plan", response_model=ExplainPlanResponse)
def explain_plan(
    request: ExplainPlanRequest,
    current_user = Depends(deps.get_current_user)
) -> Any:
    try:
        result, metadata = explainability_service.explain_plan(request.optimized_plan)
        
        return ExplainPlanResponse(
            success=True,
            data=result,
            metadata=metadata
        )
    except Exception as e:
        logger.error("Explainability service encountered a critical error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

