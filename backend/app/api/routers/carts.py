from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.cart import Cart, CartCreate, CartItem, CartItemCreate, CartItemUpdate
from app.schemas.user import User
from app.services import cart_service

router = APIRouter()

@router.get("/active", response_model=Cart)
def get_active_cart(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    cart = cart_service.get_active_cart(db, user_id=current_user.id)
    if not cart:
        # Auto-create if not exists
        cart = cart_service.create_cart(db, user_id=current_user.id, cart_in=CartCreate(name="Current Cart"))
    return cart

@router.get("/", response_model=List[Cart])
def read_carts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    return cart_service.get_carts(db, user_id=current_user.id, skip=skip, limit=limit)

@router.post("/items", response_model=CartItem)
def add_item_to_cart(
    item_in: CartItemCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Basic validation could go here (e.g. check if cart belongs to user)
    return cart_service.add_cart_item(db, item_in=item_in)

@router.put("/items/{item_id}", response_model=CartItem)
def update_item(
    item_id: int,
    item_in: CartItemUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    item = cart_service.update_cart_item(db, item_id=item_id, item_in=item_in)
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return item

@router.delete("/items/{item_id}")
def remove_item(
    item_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    success = cart_service.remove_cart_item(db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"success": True}
