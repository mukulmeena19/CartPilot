"""
Embedding generation background task.
Fetches products without embeddings and generates them in batches.
"""
from __future__ import annotations

import logging
from typing import List
from sqlalchemy.orm import Session

from app.tasks.registry import background_task
from app.providers.factory import get_embedding_provider

logger = logging.getLogger(__name__)


@background_task("generate_embeddings")
def generate_product_embeddings(db: Session, batch_size: int = 50) -> dict:
    """
    Phase 1 stub — generates embeddings for products missing them.
    Full implementation lands in Phase 6: Data Platform.
    """
    from app.db.models.product import Product

    provider = get_embedding_provider()

    products: List[Product] = (
        db.query(Product)
        .filter(Product.embedding.is_(None))
        .limit(batch_size)
        .all()
    )

    if not products:
        logger.info("No products require embedding generation.")
        return {"processed": 0}

    texts = [f"{p.name} {p.description or ''} {p.brand or ''}".strip() for p in products]
    embeddings = provider.embed(texts)

    for product, embedding in zip(products, embeddings):
        product.embedding = embedding

    db.commit()
    logger.info(f"Generated embeddings for {len(products)} products.")
    return {"processed": len(products)}
