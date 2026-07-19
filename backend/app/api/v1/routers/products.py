from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi_cache.decorator import cache
from app.api import deps
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.services import commerce_service

router = APIRouter()

@router.get("/", response_model=List[Product])
@cache(expire=300)
def read_products(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
) -> Any:
    return commerce_service.get_products(
        db, skip=skip, limit=limit, category_id=category_id, search=search
    )

@router.post("/", response_model=Product)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> Any:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return commerce_service.create_product(db, product_in=product_in)

@router.get("/{product_id}", response_model=Product)
@cache(expire=3600)
def read_product(
    product_id: int,
    db: Session = Depends(deps.get_db)
) -> Any:
    product = commerce_service.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
