import os
import sys
import time
from datetime import datetime, timezone
import structlog

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models.product import Product
from app.db.models.category import Category
from app.ai.providers.embeddings import OpenAIEmbeddingProvider
from app.ai.retrieval.document_builder import DocumentBuilder
from app.ai.retrieval.config import EMBEDDING_MODEL, EMBEDDING_VERSION

logger = structlog.get_logger(__name__)

def generate_embeddings():
    """
    Backfill / Cache script.
    Checks all active products and only generates embeddings if they are missing
    or if their embedding_version does not match the current configured version.
    """
    db = SessionLocal()
    provider = OpenAIEmbeddingProvider(model_name=EMBEDDING_MODEL)
    
    # Find products that need updating
    # Condition: embedding is null OR embedding_version != current version
    products_to_update = db.query(Product).filter(
        (Product.is_active == True) & 
        ((Product.embedding_version != EMBEDDING_VERSION) | (Product.embedding_version.is_(None)))
    ).all()
    
    if not products_to_update:
        logger.info("All products are up to date with embeddings.")
        db.close()
        return
        
    logger.info(f"Found {len(products_to_update)} products requiring embeddings.")
    
    # We will process in batches to avoid OpenAI rate limits
    BATCH_SIZE = 50
    updated_count = 0
    
    for i in range(0, len(products_to_update), BATCH_SIZE):
        batch = products_to_update[i:i+BATCH_SIZE]
        texts_to_embed = []
        
        for prod in batch:
            cat_name = prod.category.name if prod.category else "Unknown"
            doc = DocumentBuilder.build_product_document(prod, cat_name)
            texts_to_embed.append(doc)
            
        logger.info(f"Sending batch {i // BATCH_SIZE + 1} to OpenAI...")
        try:
            embeddings = provider.generate_embeddings(texts_to_embed)
            
            # Apply back to models
            now = datetime.now(timezone.utc)
            for prod, emb in zip(batch, embeddings):
                # pgvector expects a list of floats
                prod.embedding = emb
                prod.embedding_model = EMBEDDING_MODEL
                prod.embedding_version = EMBEDDING_VERSION
                prod.embedding_generated_at = now
                
            db.commit()
            updated_count += len(batch)
            logger.info(f"Successfully processed batch {i // BATCH_SIZE + 1}")
            
        except Exception as e:
            logger.error(f"Failed to process batch {i // BATCH_SIZE + 1}", error=str(e))
            db.rollback()
            
        # Slight delay to avoid aggressive rate limiting
        time.sleep(0.5)
        
    logger.info(f"Finished generating embeddings. Total updated: {updated_count}")
    db.close()

if __name__ == "__main__":
    generate_embeddings()
