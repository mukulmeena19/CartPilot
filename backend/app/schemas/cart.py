from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from .product import Product

class CartItemBase(BaseModel):
    product_id: int
    quantity: int
    price_at_add: float
    ai_explanation: Optional[str] = None
    is_verified: bool = True

class CartItemCreate(CartItemBase):
    cart_id: int

class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None

class CartItem(CartItemBase):
    id: int
    cart_id: int
    product: Optional[Product] = None

    model_config = ConfigDict(from_attributes=True)

class CartBase(BaseModel):
    name: Optional[str] = None
    is_active: bool = True

class CartCreate(CartBase):
    pass

class CartUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class Cart(CartBase):
    id: int
    user_id: int
    total_amount: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[CartItem] = []

    model_config = ConfigDict(from_attributes=True)
