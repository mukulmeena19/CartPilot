from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.services import commerce_service

router = APIRouter()

@router.get("/", response_model=List[Category])
def read_categories(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return commerce_service.get_categories(db, skip=skip, limit=limit)

@router.post("/", response_model=Category)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> Any:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return commerce_service.create_category(db, category_in=category_in)

@router.get("/{category_id}", response_model=Category)
def read_category(
    category_id: int,
    db: Session = Depends(deps.get_db)
) -> Any:
    category = commerce_service.get_category(db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
