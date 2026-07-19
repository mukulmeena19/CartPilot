"""
ETL pipeline for Open Food Facts.
Downloads raw JSONL data, normalizes it, and inserts into PostgreSQL.
"""
from __future__ import annotations

import logging
import json
import asyncio
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.tasks.registry import background_task
from app.db.models.product import Product

logger = logging.getLogger(__name__)


@background_task("etl_open_food_facts")
def import_open_food_facts(db: Session, file_path: str) -> dict:
    """
    Reads a local JSONL file of Open Food Facts dump and loads into DB.
    Expected format per line:
    { "product_name": "...", "brands": "...", "categories": "...", ... }
    """
    logger.info(f"Starting ETL for Open Food Facts from {file_path}")
    
    processed = 0
    inserted = 0
    batch_size = 500
    batch: List[Product] = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                processed += 1
                try:
                    data = json.loads(line)
                    name = data.get("product_name")
                    if not name:
                        continue

                    # Basic normalization
                    brand = data.get("brands", "")
                    description = data.get("ingredients_text", "")
                    image_url = data.get("image_url", "")
                    categories = data.get("categories", "")

                    # Fallback pricing (Open Food Facts doesn't have prices)
                    price = 4.99 

                    product = Product(
                        name=name.strip(),
                        brand=brand.strip()[:100] if brand else None,
                        description=description.strip() if description else None,
                        price=price,
                        category_id=1,  # Generic category for now
                        image_url=image_url if image_url else None,
                        is_active=True
                    )
                    batch.append(product)

                    if len(batch) >= batch_size:
                        db.bulk_save_objects(batch)
                        db.commit()
                        inserted += len(batch)
                        batch.clear()

                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON at line {processed}")
                    continue

        if batch:
            db.bulk_save_objects(batch)
            db.commit()
            inserted += len(batch)

        logger.info(f"ETL Complete: {processed} processed, {inserted} inserted.")
        return {"processed": processed, "inserted": inserted}

    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return {"error": "file_not_found"}
