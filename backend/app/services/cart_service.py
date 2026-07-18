from sqlalchemy.orm import Session
from app.db.models.cart import Cart, CartItem
from app.db.models.order import Order
from app.schemas.cart import CartCreate, CartUpdate, CartItemCreate, CartItemUpdate
from app.schemas.order import OrderCreate, OrderUpdate
from typing import List, Optional

# --- CART SERVICES ---
def create_cart(db: Session, user_id: int, cart_in: CartCreate) -> Cart:
    db_obj = Cart(user_id=user_id, **cart_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_active_cart(db: Session, user_id: int) -> Optional[Cart]:
    return db.query(Cart).filter(Cart.user_id == user_id, Cart.is_active == True).first()

def get_carts(db: Session, user_id: int, skip: int = 0, limit: int = 10) -> List[Cart]:
    return db.query(Cart).filter(Cart.user_id == user_id).offset(skip).limit(limit).all()

def add_cart_item(db: Session, item_in: CartItemCreate) -> CartItem:
    db_obj = CartItem(**item_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    update_cart_total(db, item_in.cart_id)
    return db_obj

def update_cart_item(db: Session, item_id: int, item_in: CartItemUpdate) -> Optional[CartItem]:
    db_obj = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not db_obj:
        return None
    if item_in.quantity is not None:
        db_obj.quantity = item_in.quantity
    db.commit()
    db.refresh(db_obj)
    update_cart_total(db, db_obj.cart_id)
    return db_obj

def remove_cart_item(db: Session, item_id: int) -> bool:
    db_obj = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not db_obj:
        return False
    cart_id = db_obj.cart_id
    db.delete(db_obj)
    db.commit()
    update_cart_total(db, cart_id)
    return True

def update_cart_total(db: Session, cart_id: int):
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if cart:
        total = sum(item.quantity * item.price_at_add for item in cart.items)
        cart.total_amount = total
        db.commit()

# --- ORDER SERVICES ---
def create_order(db: Session, user_id: int, order_in: OrderCreate) -> Order:
    db_obj = Order(user_id=user_id, **order_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # Mark cart as inactive once ordered
    if order_in.cart_id:
        cart = db.query(Cart).filter(Cart.id == order_in.cart_id).first()
        if cart:
            cart.is_active = False
            db.commit()
            
    return db_obj

def get_orders(db: Session, user_id: int, skip: int = 0, limit: int = 10) -> List[Order]:
    return db.query(Order).filter(Order.user_id == user_id).offset(skip).limit(limit).all()
