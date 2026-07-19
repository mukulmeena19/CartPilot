"""
Synthetic Restaurant & MenuItem Data Generator.
Used to bootstrap the Food Ordering domain before real merchant integration.
"""
from __future__ import annotations

import logging
import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.tasks.registry import background_task
from app.db.models.restaurant import Restaurant, MenuItem

logger = logging.getLogger(__name__)


CUISINES = ["Indian", "Chinese", "Italian", "Mexican", "American", "Healthy"]
RESTAURANT_PREFIXES = ["The Great", "Spicy", "Golden", "Royal", "Urban", "Authentic"]
RESTAURANT_SUFFIXES = ["Bistro", "Diner", "Kitchen", "Express", "House", "Eatery"]

MENU_ITEMS = {
    "Indian": [("Butter Chicken", 15.99), ("Garlic Naan", 3.99), ("Dal Makhani", 12.99), ("Paneer Tikka", 14.99)],
    "Chinese": [("Kung Pao Chicken", 14.99), ("Fried Rice", 10.99), ("Spring Rolls", 5.99), ("Dim Sum", 8.99)],
    "Italian": [("Margherita Pizza", 16.99), ("Pasta Carbonara", 18.99), ("Tiramisu", 7.99), ("Garlic Bread", 4.99)],
    "Mexican": [("Chicken Tacos", 11.99), ("Beef Burrito", 13.99), ("Guacamole & Chips", 6.99), ("Quesadilla", 10.99)],
    "American": [("Cheeseburger", 12.99), ("French Fries", 4.99), ("Milkshake", 5.99), ("BBQ Ribs", 21.99)],
    "Healthy": [("Quinoa Salad", 13.99), ("Acai Bowl", 10.99), ("Green Smoothie", 7.99), ("Grilled Salmon", 22.99)],
}


@background_task("generate_synthetic_restaurants")
def generate_restaurants(db: Session, count: int = 50) -> dict:
    """
    Generates synthetic restaurants and menu items to bootstrap the catalog.
    """
    logger.info(f"Starting synthetic generation for {count} restaurants.")
    inserted = 0

    for _ in range(count):
        cuisine = random.choice(CUISINES)
        prefix = random.choice(RESTAURANT_PREFIXES)
        suffix = random.choice(RESTAURANT_SUFFIXES)
        name = f"{prefix} {cuisine} {suffix}"

        restaurant = Restaurant(
            name=name,
            description=f"Authentic {cuisine} cuisine serving the best dishes in town.",
            city="Metropolis",
            is_active=True,
            is_open=True,
            rating=round(random.uniform(3.5, 4.9), 1),
            total_ratings=random.randint(10, 500),
            delivery_time_estimate=random.randint(20, 60),
            cuisine_tags=[cuisine]
        )
        db.add(restaurant)
        db.commit()
        db.refresh(restaurant)

        # Generate Menu Items
        items_to_add = MENU_ITEMS[cuisine]
        for item_name, price in items_to_add:
            menu_item = MenuItem(
                restaurant_id=restaurant.id,
                name=item_name,
                description=f"Delicious {item_name} prepared fresh.",
                price=price,
                cuisine=cuisine,
                is_vegetarian="Paneer" in item_name or "Dal" in item_name or "Salad" in item_name or "Margherita" in item_name,
                is_available=True
            )
            db.add(menu_item)

        db.commit()
        inserted += 1

    logger.info(f"Generated {inserted} synthetic restaurants.")
    return {"inserted": inserted}
