from typing import Any
from fastapi import APIRouter, Depends
from app.api import deps
from app.db.models.user import User as DBUser
from app.schemas.user import User as UserSchema

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: DBUser = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user profile.
    """
    return current_user
