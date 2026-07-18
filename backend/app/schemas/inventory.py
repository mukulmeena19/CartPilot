from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class InventoryBase(BaseModel):
    product_id: int
    stock_quantity: int
    merchant: str = "CartPilot Store"
    is_available: int = 1

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    stock_quantity: Optional[int] = None
    is_available: Optional[int] = None
    last_restocked: Optional[datetime] = None

class Inventory(InventoryBase):
    id: int
    last_restocked: Optional[datetime] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
