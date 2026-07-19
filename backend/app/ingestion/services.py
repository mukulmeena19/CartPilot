import json
import time
from typing import Any
from sqlalchemy.orm import Session
from app.ingestion.parser import OpenFoodFactsParser
from app.ingestion.validator import Validator
from app.ingestion.cleaner import Cleaner
from app.ingestion.embedder import Embedder
from app.ingestion.repository import Repository

class OpenFoodFactsIngestionService:
    def __init__(self, db: Session):
        self.parser = OpenFoodFactsParser()
        self.validator = Validator()
        self.cleaner = Cleaner()
        self.embedder = Embedder()
        self.repository = Repository(db)

    def run(self, raw_data: Any):
        print("Starting ingestion pipeline...")
        start_time = time.time()
        
        # 1. Parse
        print("Parsing raw data...")
        parsed_items = self.parser.parse(raw_data)
        total_parsed = len(parsed_items)
        print(f"Parsed {total_parsed} items.")
        
        # 2. Validate
        print("Validating items...")
        valid_items = self.validator.validate_openfoodfacts(parsed_items)
        total_valid = len(valid_items)
        print(f"Validated {total_valid} items (Skipped {total_parsed - total_valid}).")
        
        if not valid_items:
            print("No valid items to process.")
            return

        # 3. Clean
        print("Cleaning items...")
        cleaned_items = self.cleaner.clean_openfoodfacts(valid_items)
        
        # 4. Embed and Insert in Batches
        batch_size = 500
        total_processed = 0
        
        for i in range(0, len(cleaned_items), batch_size):
            batch = cleaned_items[i:i + batch_size]
            
            print(f"Embedding batch {i // batch_size + 1} ({len(batch)} items)...")
            embedded_batch = self.embedder.embed_openfoodfacts(batch)
            
            print("Inserting batch into database...")
            self.repository.upsert_products(embedded_batch)
            
            total_processed += len(batch)
            print(f"Progress: {total_processed}/{total_valid} items processed.")
            
        elapsed_time = time.time() - start_time
        print(f"Ingestion completed in {elapsed_time:.2f} seconds.")
        print(f"Total rows: {total_parsed} | Processed: {total_processed} | Skipped: {total_parsed - total_processed}")
