import os
import sys
from sqlalchemy.orm import Session

# Add the root 'backend' directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models.category import Category
from app.db.models.product import Product
from app.db.models.inventory import Inventory

CATEGORIES = [
    {"name": "Produce", "description": "Fresh fruits and vegetables"},
    {"name": "Dairy & Eggs", "description": "Milk, cheese, butter, and eggs"},
    {"name": "Meat & Seafood", "description": "Chicken, beef, fish, etc."},
    {"name": "Pantry", "description": "Rice, pasta, spices, canned goods"},
    {"name": "Bakery", "description": "Breads, pastries, and sweets"},
]

PRODUCTS = [
    {"name": "Organic Bananas", "brand": "Nature's Best", "category_id": 1, "price": 0.59, "unit": "kg", "description": "Fresh organic bananas."},
    {"name": "Whole Milk 1 Gallon", "brand": "Dairy Pure", "category_id": 2, "price": 3.49, "unit": "gallon", "description": "Fresh whole milk."},
    {"name": "Boneless Skinless Chicken Breasts", "brand": "Farm Fresh", "category_id": 3, "price": 5.99, "unit": "lb", "description": "Lean chicken breasts."},
    {"name": "Basmati Rice 5kg", "brand": "Royal", "category_id": 4, "price": 12.99, "unit": "bag", "description": "Long grain aromatic rice."},
    {"name": "Garam Masala", "brand": "Everest", "category_id": 4, "price": 4.50, "unit": "100g", "description": "Indian spice blend."},
    {"name": "Whole Wheat Bread", "brand": "Nature's Own", "category_id": 5, "price": 2.99, "unit": "loaf", "description": "Healthy whole wheat bread."},
    {"name": "Butter 500g", "brand": "Amul", "category_id": 2, "price": 4.50, "unit": "box", "description": "Pasteurized butter."},
]

def seed_db():
    print("Starting database seed...")
    db: Session = SessionLocal()
    try:
        # Seed Categories
        for cat_data in CATEGORIES:
            existing = db.query(Category).filter_by(name=cat_data["name"]).first()
            if not existing:
                cat = Category(**cat_data)
                db.add(cat)
        db.commit()
        print("Categories seeded.")

        # Seed Products & Inventory
        for prod_data in PRODUCTS:
            existing = db.query(Product).filter_by(name=prod_data["name"]).first()
            if not existing:
                prod = Product(**prod_data)
                db.add(prod)
                db.commit()
                db.refresh(prod)
                
                # Add default inventory
                inv = Inventory(product_id=prod.id, stock_quantity=100)
                db.add(inv)
        db.commit()
        print("Products and Inventory seeded.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
