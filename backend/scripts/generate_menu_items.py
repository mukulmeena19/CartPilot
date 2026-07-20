import os
import sys
import json
import time
import structlog
from typing import List
from pydantic import BaseModel, Field

# Add backend to path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models.restaurant import Restaurant, MenuItem
from app.ai.providers.gemini_provider import GeminiProvider

logger = structlog.get_logger(__name__)

RAW_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw", "restaurant_costs.json")

class GeneratedMenuItem(BaseModel):
    name: str = Field(description="Name of the dish")
    price: float = Field(description="Price in INR")
    description: str = Field(description="Short delicious description")
    category: str = Field(description="E.g., Main Course, Starter, Beverage, Dessert")
    is_vegetarian: bool
    is_vegan: bool
    is_gluten_free: bool

class MenuOutput(BaseModel):
    items: List[GeneratedMenuItem]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_menus():
    logger.info("Initializing Gemini Provider...")
    try:
        provider = GeminiProvider()
    except Exception as e:
        logger.error(f"Failed to init Gemini Provider: {e}")
        return

    # Load cost mapping
    cost_mapping = {}
    if os.path.exists(RAW_DATA_PATH):
        with open(RAW_DATA_PATH, "r") as f:
            cost_mapping = json.load(f)

    db = next(get_db())

    # Get all restaurants that don't have menu items (idempotent)
    # Using a subquery or join to find them
    # For simplicity, we can query all restaurants and check if they have items
    restaurants = db.query(Restaurant).all()
    logger.info(f"Total restaurants in DB: {len(restaurants)}")

    processed_count = 0
    skipped_count = 0
    error_count = 0

    for idx, restaurant in enumerate(restaurants):
        # Check if already has menu items
        existing_items = db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant.id).first()
        if existing_items:
            skipped_count += 1
            continue

        avg_cost = cost_mapping.get(restaurant.name, 500.0) # default to 500 if not found
        cuisine_str = ", ".join(restaurant.cuisine_tags) if restaurant.cuisine_tags else "General Indian"

        system_prompt = """
        You are a restaurant menu generator. You will receive the restaurant's cuisines and their average cost for two people.
        You must output exactly 8 to 12 realistic menu items for this restaurant.
        Prices for individual dishes should make mathematical sense given the average cost for two people.
        """

        user_prompt = f"Restaurant cuisines: {cuisine_str}\nAverage cost for two: ₹{avg_cost}"

        try:
            result, metadata = provider.generate_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=MenuOutput
            )

            db_items = []
            for item in result.items:
                mi = MenuItem(
                    restaurant_id=restaurant.id,
                    name=item.name,
                    description=item.description,
                    price=item.price,
                    category=item.category,
                    cuisine=restaurant.cuisine_tags[0] if restaurant.cuisine_tags else None,
                    is_vegetarian=item.is_vegetarian,
                    is_vegan=item.is_vegan,
                    is_gluten_free=item.is_gluten_free,
                    tags=["ai_generated"]
                )
                db_items.append(mi)
            
            db.add_all(db_items)
            db.commit()
            processed_count += 1
            
            if processed_count % 50 == 0:
                logger.info(f"Progress: Generated menus for {processed_count} restaurants (Skipped: {skipped_count}, Errors: {error_count})")
            
            # Sleep to respect rate limits (Gemini free tier allows 15 RPM = 4 seconds per request)
            # We'll sleep 4.5 seconds to be safe.
            time.sleep(4.5)
            
        except Exception as e:
            logger.error(f"Failed to generate for {restaurant.name}: {str(e)}")
            error_count += 1
            # If it's a rate limit error (429), we should probably sleep longer
            if "429" in str(e):
                logger.warning("Rate limit hit, sleeping for 60 seconds...")
                time.sleep(60)

    logger.info(f"Finished generating menus! Processed: {processed_count}, Skipped: {skipped_count}, Errors: {error_count}")

if __name__ == "__main__":
    generate_menus()
