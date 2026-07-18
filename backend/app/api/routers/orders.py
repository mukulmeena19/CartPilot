from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.order import Order, OrderCreate
from app.schemas.user import User
from app.services import cart_service

router = APIRouter()

@router.post("/", response_model=Order)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    return cart_service.create_order(db, user_id=current_user.id, order_in=order_in)

@router.get("/", response_model=List[Order])
def read_orders(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    return cart_service.get_orders(db, user_id=current_user.id, skip=skip, limit=limit)
