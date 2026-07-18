from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here so Alembic can discover them
from app.db.models.user import User
from app.db.models.token import RefreshToken
from app.db.models.category import Category
from app.db.models.product import Product
from app.db.models.inventory import Inventory
from app.db.models.cart import Cart, CartItem
from app.db.models.order import Order
