import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import random
import uuid
from decimal import Decimal
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.product import Product

# Some sample grocery data
SEED_PRODUCTS = [
    {"name": "Whole Milk", "brand": "Amul", "category": "Dairy", "price": 60.0, "dietary": ["vegetarian"]},
    {"name": "Paneer", "brand": "Amul", "category": "Dairy", "price": 85.0, "dietary": ["vegetarian", "high_protein"]},
    {"name": "Greek Yogurt", "brand": "Epigamia", "category": "Dairy", "price": 70.0, "dietary": ["vegetarian", "high_protein"]},
    {"name": "Eggs", "brand": "Farm Fresh", "category": "Dairy", "price": 65.0, "dietary": ["high_protein"]},
    {"name": "Whole Wheat Bread", "brand": "Britannia", "category": "Bakery", "price": 45.0, "dietary": ["vegetarian"]},
    {"name": "Oats", "brand": "Quaker", "category": "Cereals", "price": 120.0, "dietary": ["vegetarian", "vegan"]},
    {"name": "Almonds", "brand": "Happilo", "category": "Snacks", "price": 250.0, "dietary": ["vegetarian", "vegan", "keto"]},
    {"name": "Chicken Breast", "brand": "Licious", "category": "Meat", "price": 300.0, "dietary": ["high_protein", "keto"]},
    {"name": "Broccoli", "brand": "Fresh", "category": "Vegetables", "price": 40.0, "dietary": ["vegetarian", "vegan"]},
    {"name": "Spinach", "brand": "Fresh", "category": "Vegetables", "price": 30.0, "dietary": ["vegetarian", "vegan"]},
    {"name": "Brown Rice", "brand": "Daawat", "category": "Pantry", "price": 150.0, "dietary": ["vegetarian", "vegan"]},
    {"name": "Tofu", "brand": "Morinaga", "category": "Dairy", "price": 110.0, "dietary": ["vegetarian", "vegan", "high_protein"]},
]

def generate_dummy_embedding(dim=1536):
    """Generates a dummy normalized vector for pgvector."""
    vec = [random.uniform(-1, 1) for _ in range(dim)]
    norm = sum(x**2 for x in vec) ** 0.5
    return [x / norm for x in vec]

def seed_catalog(size: int):
    db: Session = SessionLocal()
    try:
        # Clear existing
        db.query(Product).delete()
        
        products_to_add = []
        for i in range(size):
            base = SEED_PRODUCTS[i % len(SEED_PRODUCTS)]
            prod = Product(
                id=str(uuid.uuid4()),
                name=f"{base['name']} - Variant {i}" if i >= len(SEED_PRODUCTS) else base['name'],
                brand=base['brand'],
                category=base['category'],
                description=f"Fresh {base['name']} from {base['brand']}",
                price=Decimal(str(base['price'] + random.uniform(-10, 20))),
                inventory_count=random.randint(0, 100),
                dietary_labels=base['dietary'],
                tags=[base['category'].lower()],
                metadata_json={},
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
    parser.add_argument("--size", type=int, default=50, help="Number of products to generate.")
    args = parser.parse_args()
    
    seed_catalog(args.size)
