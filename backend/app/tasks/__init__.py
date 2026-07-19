from app.tasks.registry import background_task, get_task
from app.tasks.embeddings import generate_product_embeddings
from app.tasks.etl_food import import_open_food_facts
from app.tasks.etl_restaurant import generate_restaurants

__all__ = [
    "background_task",
    "get_task",
    "generate_product_embeddings",
    "import_open_food_facts",
    "generate_restaurants"
]
