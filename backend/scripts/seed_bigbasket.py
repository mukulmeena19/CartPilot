import os
import sys
import glob
import pandas as pd
import structlog
import time
import math
import random
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

# Add backend to path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import Base
from app.db.session import SessionLocal
from app.db.models.category import Category
from app.db.models.product import Product
from app.db.models.inventory import Inventory
from app.core.embeddings import embedding_service
from app.core.config import settings

logger = structlog.get_logger(__name__)

RAW_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw", "bigbasket_catalog")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def parse_price(mrp_str):
    try:
        if pd.isna(mrp_str):
            return None
        mrp_str = str(mrp_str).replace('₹', '').replace(',', '').strip()
        return float(mrp_str)
    except Exception:
        return None

def clean_desc(desc):
    if pd.isna(desc):
        return ""
    desc = str(desc)
    if len(desc) > 500:
        return desc[:497] + "..."
    return desc

def process_catalog():
    if not os.path.exists(RAW_DATA_PATH):
        logger.error(f"Path not found: {RAW_DATA_PATH}")
        return

    excel_files = glob.glob(os.path.join(RAW_DATA_PATH, "**", "*.xlsx"), recursive=True)
    if not excel_files:
        logger.error(f"No .xlsx files found in {RAW_DATA_PATH}")
        return
        
    logger.info(f"Found {len(excel_files)} Excel files. Loading into memory...")

    dfs = []
    for f in excel_files:
        try:
            df = pd.read_excel(f)
            dfs.append(df)
        except Exception as e:
            logger.error(f"Failed to read {f}: {e}")

    if not dfs:
        return

    full_df = pd.concat(dfs, ignore_index=True)
    logger.info(f"Total rows loaded: {len(full_df)}")

    db = next(get_db())
    
    # 1. Process Categories
    logger.info("Extracting categories...")
    # Map Sub-sub-Category, fallback to Sub-Category
    full_df['Final_Category'] = full_df['Sub-sub-Category'].fillna(full_df['Sub-Category'])
    full_df = full_df.dropna(subset=['Final_Category'])
    
    unique_cats = full_df['Final_Category'].unique()
    
    # Insert categories
    cat_map = {}
    for c in unique_cats:
        c_str = str(c).strip()
        if not c_str:
            continue
        db_cat = db.query(Category).filter(Category.name == c_str).first()
        if not db_cat:
            db_cat = Category(name=c_str, description=f"Products in {c_str}")
            db.add(db_cat)
            db.commit()
            db.refresh(db_cat)
        cat_map[c_str] = db_cat.id

    # 2. Process Products
    logger.info("Extracting products...")
    records = full_df.to_dict('records')
    
    # We will pick 5000 random items to embed, stratified by category
    # First, group items by category
    cat_to_items = {}
    for r in records:
        cat_name = str(r.get('Final_Category', '')).strip()
        if not cat_name or cat_name not in cat_map:
            continue
        price = parse_price(r.get('MRP'))
        if price is None:
            continue # skip malformed
        
        if cat_name not in cat_to_items:
            cat_to_items[cat_name] = []
        cat_to_items[cat_name].append(r)
        
    total_valid = sum(len(items) for items in cat_to_items.values())
    logger.info(f"Total valid products with prices: {total_valid}")
    
    # Calculate how many to sample per category
    sample_size = 5000
    sampled_records = []
    unsampled_records = []
    
    if total_valid <= sample_size:
        # Just use all
        for items in cat_to_items.values():
            sampled_records.extend(items)
    else:
        for cat_name, items in cat_to_items.items():
            cat_sample_count = math.ceil((len(items) / total_valid) * sample_size)
            random.shuffle(items)
            sampled_records.extend(items[:cat_sample_count])
            unsampled_records.extend(items[cat_sample_count:])
            
    # Trim exactly to 5000 if math.ceil gave slightly more
    random.shuffle(sampled_records)
    if len(sampled_records) > sample_size:
        unsampled_records.extend(sampled_records[sample_size:])
        sampled_records = sampled_records[:sample_size]
        
    logger.info(f"Selected {len(sampled_records)} records for embedding (is_active=True).")
    logger.info(f"Remaining {len(unsampled_records)} records will be is_active=False without embeddings.")
    
    # Helper to insert products
    def insert_products(recs, is_active=False, generate_embeddings=False):
        batch_size = 50
        skipped = 0
        inserted = 0
        
        for i in range(0, len(recs), batch_size):
            batch = recs[i:i+batch_size]
            db_products = []
            texts_to_embed = []
            valid_batch_recs = []
            
            for r in batch:
                cat_name = str(r.get('Final_Category')).strip()
                price = parse_price(r.get('MRP'))
                
                db_prod = Product(
                    name=str(r.get('SKU Name', '')),
                    brand=str(r.get('Brand', '')) if not pd.isna(r.get('Brand')) else None,
                    category_id=cat_map[cat_name],
                    price=price,
                    unit=str(r.get('SKU Size', '')),
                    description=clean_desc(r.get('About the Product')),
                    image_url=str(r.get('Image Link', '')) if not pd.isna(r.get('Image Link')) else None,
                    is_active=is_active,
                    embedding_model=settings.EMBEDDING_MODEL if generate_embeddings else None
                )
                db_products.append(db_prod)
                valid_batch_recs.append(r)
                if generate_embeddings:
                    # Create embedding text
                    text = f"{db_prod.name} {db_prod.brand or ''} {db_prod.description or ''} {cat_name}"
                    texts_to_embed.append(text)
            
            if generate_embeddings and texts_to_embed:
                try:
                    embeddings = embedding_service.embed_documents(texts_to_embed)
                    for j, emb in enumerate(embeddings):
                        db_products[j].embedding = emb
                except Exception as e:
                    logger.error(f"Failed to embed batch: {e}")
                    # Save them without embeddings but inactive
                    for p in db_products:
                        p.is_active = False
            
            for p in db_products:
                db.add(p)
            db.commit()
            inserted += len(db_products)
            
            if (i + batch_size) % 500 == 0:
                logger.info(f"Processed {inserted} / {len(recs)} records...")
        
        return inserted, skipped

    # Insert unsampled first (faster)
    logger.info("Inserting inactive products...")
    insert_products(unsampled_records, is_active=False, generate_embeddings=False)
    
    # Insert sampled
    logger.info("Inserting active products and generating embeddings (this will take a while)...")
    insert_products(sampled_records, is_active=True, generate_embeddings=True)

    logger.info("Finished seeding BigBasket data!")

if __name__ == "__main__":
    process_catalog()
