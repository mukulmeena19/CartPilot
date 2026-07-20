import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import random
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

# Import ALL models so metadata resolves
from app.db.models.user import User
from app.db.models.token import RefreshToken
from app.db.models.category import Category
from app.db.models.product import Product
from app.db.models.inventory import Inventory
from app.db.models.cart import Cart, CartItem
from app.db.models.order import Order
from app.db.models.restaurant import Restaurant, MenuItem
from app.db.models.chat import ChatSession, ChatMessage
from app.db.models.knowledge import Recipe, Ingredient, RecipeIngredient, Substitution
from app.db.models.intelligence import TasteProfile, UserPreference, BehavioralHistory, RecommendationFeedback
from app.db.models.analytics import AnalyticsEvent, TrendSnapshot, MarketBasketAssociation

SEED_PRODUCTS = [
    {"name": "Whole Milk", "brand": "Amul", "category": "Dairy", "price": 60.0, "unit": "liter"},
    {"name": "Paneer", "brand": "Amul", "category": "Dairy", "price": 85.0, "unit": "200g"},
    {"name": "Greek Yogurt", "brand": "Epigamia", "category": "Dairy", "price": 70.0, "unit": "cup"},
    {"name": "Eggs", "brand": "Farm Fresh", "category": "Dairy", "price": 65.0, "unit": "dozen"},
    {"name": "Whole Wheat Bread", "brand": "Britannia", "category": "Bakery", "price": 45.0, "unit": "loaf"},
    {"name": "Oats", "brand": "Quaker", "category": "Cereals", "price": 120.0, "unit": "1kg"},
    {"name": "Almonds", "brand": "Happilo", "category": "Snacks", "price": 250.0, "unit": "250g"},
    {"name": "Chicken Breast", "brand": "Licious", "category": "Meat", "price": 300.0, "unit": "500g"},
    {"name": "Broccoli", "brand": "Fresh", "category": "Vegetables", "price": 40.0, "unit": "head"},
    {"name": "Spinach", "brand": "Fresh", "category": "Vegetables", "price": 30.0, "unit": "bunch"},
    {"name": "Brown Rice", "brand": "Daawat", "category": "Pantry", "price": 150.0, "unit": "1kg"},
    {"name": "Tofu", "brand": "Morinaga", "category": "Dairy", "price": 110.0, "unit": "packet"},
]

def generate_dummy_embedding(dim=384): # using 384 for MiniLM default
    vec = [random.uniform(-1, 1) for _ in range(dim)]
    norm = sum(x**2 for x in vec) ** 0.5
    return [x / norm for x in vec]

def seed_catalog(size: int):
    # Ensure all tables exist before seeding
    from app.db.base import Base
    from app.db.session import engine
    
    print("Creating all tables in the database...")
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
    
    db: Session = SessionLocal()
    try:
        print("Clearing existing data...")
        # Clear existing
        db.query(Product).delete()
        db.query(Category).delete()
        
        # Create categories
        categories_dict = {}
        unique_cats = set(p['category'] for p in SEED_PRODUCTS)
        for cat_name in unique_cats:
            cat = Category(name=cat_name)
            db.add(cat)
            db.flush()
            categories_dict[cat_name] = cat.id
            
        products_to_add = []
        for i in range(size):
            base = SEED_PRODUCTS[i % len(SEED_PRODUCTS)]
            prod = Product(
                name=f"{base['name']} - Variant {i}" if i >= len(SEED_PRODUCTS) else base['name'],
                brand=base['brand'],
                category_id=categories_dict[base['category']],
                description=f"Fresh {base['name']} from {base['brand']}",
                price=float(base['price'] + random.uniform(-10, 20)),
                unit=base['unit'],
                is_active=True,
                embedding=generate_dummy_embedding()
            )
            products_to_add.append(prod)
            
        db.add_all(products_to_add)
        db.commit()
        print(f"Successfully seeded {size} products into the catalog.")
        
    except Exception as e:
        print(f"Failed to seed catalog: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the CartPilot Product Catalog.")
    parser.add_argument("--size", type=int, default=500, help="Number of products to generate.")
    args = parser.parse_args()
    
    seed_catalog(args.size)
