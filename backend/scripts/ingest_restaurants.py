import sys
import os
import logging
from pathlib import Path

# Add backend to path so we can import app
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.db.models.restaurant import Restaurant, MenuItem
from app.core.embeddings import embedding_service
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    mock_restaurants = [
        {
            "id": "rest_1",
            "name": "Healthy Bites",
            "cuisine_type": "Healthy, Salads",
            "rating": 4.8,
            "delivery_time_mins": 25,
            "dietary_tags": ["Vegetarian", "Vegan", "Gluten-Free"],
            "menu": [
                {"name": "Quinoa Salad", "price": 250.0, "calories": 300},
                {"name": "Green Smoothie", "price": 150.0, "calories": 150}
            ]
        },
        {
            "id": "rest_2",
            "name": "Protein House",
            "cuisine_type": "American, Grill",
            "rating": 4.5,
            "delivery_time_mins": 40,
            "dietary_tags": ["High Protein", "Keto"],
            "menu": [
                {"name": "Grilled Chicken Breast", "price": 400.0, "calories": 450},
                {"name": "Steak Bowl", "price": 600.0, "calories": 600}
            ]
        }
    ]
    
    db = SessionLocal()
    try:
        for r_data in mock_restaurants:
            restaurant = db.query(Restaurant).filter(Restaurant.id == r_data["id"]).first()
            if not restaurant:
                restaurant = Restaurant(id=r_data["id"])
            
            restaurant.name = r_data["name"]
            restaurant.cuisine_type = r_data["cuisine_type"]
            restaurant.rating = r_data["rating"]
            restaurant.delivery_time_mins = r_data["delivery_time_mins"]
            restaurant.dietary_tags = r_data["dietary_tags"]
            
            # Embed
            doc = (
                f"Restaurant: {r_data['name']}\n"
                f"Cuisine: {r_data['cuisine_type']}\n"
                f"Tags: {', '.join(r_data['dietary_tags'])}\n"
                f"Menu Highlights: {', '.join([m['name'] for m in r_data['menu']])}"
            )
            embedding = embedding_service.embed_documents([doc])[0]
            restaurant.embedding = embedding
            
            # Simplified insertion for demo purposes without explicit check if in session
            # using merge to handle both insert and update
            db.merge(restaurant)
                
        db.commit()
        logger.info(f"Successfully ingested {len(mock_restaurants)} restaurants.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
