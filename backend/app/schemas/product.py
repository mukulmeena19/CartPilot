from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from .category import Category

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    brand: Optional[str] = None
    category_id: int
    price: float
    unit: str
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = None
    unit: Optional[str] = None
    image_url: Optional[str] = None

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Optional nested relationships
    category: Optional[Category] = None

    model_config = ConfigDict(from_attributes=True)
