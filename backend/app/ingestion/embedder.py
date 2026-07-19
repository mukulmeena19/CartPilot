from typing import List, Dict, Any
from app.core.embeddings import embedding_service
from app.core.config import settings

class Embedder:
    def embed_openfoodfacts(self, cleaned_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Format structured documents
        documents = []
        for item in cleaned_items:
            doc = (
                f"Product: {item['name']}\n"
                f"Brand: {item['brand']}\n"
                f"Category: {item['category_name']}\n"
                f"Nutrition: Protein {item['nutrition']['protein']}g, Calories {item['nutrition']['calories']}kcal\n"
                f"Description: {item['description']}"
            )
            documents.append(doc)
            
        # Batch embed
        # the sentence transformer model can handle large batches, but we might want to chunk it if it's huge.
        # Assuming cleaned_items is already a reasonable batch size (e.g. 500)
        
        embeddings = embedding_service.embed_documents(documents)
        
        # Attach embeddings back to items
        for i, item in enumerate(cleaned_items):
            item['embedding'] = embeddings[i]
            item['embedding_model'] = settings.EMBEDDING_MODEL
            item['embedding_version'] = "1.0"
            
        return cleaned_items
