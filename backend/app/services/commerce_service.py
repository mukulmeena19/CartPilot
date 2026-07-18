from sqlalchemy.orm import Session
from app.db.models.category import Category
from app.db.models.product import Product
from app.db.models.inventory import Inventory
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.product import ProductCreate, ProductUpdate
from app.schemas.inventory import InventoryCreate, InventoryUpdate
from typing import List, Optional

# --- CATEGORY SERVICES ---
def create_category(db: Session, category_in: CategoryCreate) -> Category:
    db_obj = Category(name=category_in.name, description=category_in.description)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    return db.query(Category).offset(skip).limit(limit).all()

def get_category(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()

# --- PRODUCT SERVICES ---
def create_product(db: Session, product_in: ProductCreate) -> Product:
    db_obj = Product(**product_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_products(db: Session, skip: int = 0, limit: int = 100, category_id: Optional[int] = None, search: Optional[str] = None) -> List[Product]:
    query = db.query(Product)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

def get_product(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()

# --- INVENTORY SERVICES ---
def create_inventory(db: Session, inventory_in: InventoryCreate) -> Inventory:
    db_obj = Inventory(**inventory_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_inventory(db: Session, product_id: int, inventory_in: InventoryUpdate) -> Optional[Inventory]:
    db_obj = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not db_obj:
        return None
    update_data = inventory_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_inventory(db: Session, product_id: int) -> Optional[Inventory]:
    return db.query(Inventory).filter(Inventory.product_id == product_id).first()
