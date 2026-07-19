import os
from typing import List
from functools import lru_cache
from app.core.config import settings

class EmbeddingService:
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
        
        if "MiniLM" in self.model_name or "bge" in self.model_name:
            # Local sentence-transformers model
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.provider = "local"
        else:
            # Use Gemini or Google API
            import google.generativeai as genai
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is required for Gemini embeddings")
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model_name = self.model_name if "models/" in self.model_name else f"models/{self.model_name}"
            self.provider = "gemini"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self.provider == "local":
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        elif self.provider == "gemini":
            import google.generativeai as genai
            response = genai.embed_content(
                model=self.model_name,
                content=texts,
                task_type="retrieval_document"
            )
            # The API might return a single embedding or a list depending on input
            if isinstance(texts, str) or len(texts) == 1:
                return [response['embedding']] if isinstance(texts, str) else [response['embedding'][0]]
            return response['embedding']

    @lru_cache(maxsize=1024)
    def embed_query(self, text: str) -> List[float]:
        if self.provider == "local":
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        elif self.provider == "gemini":
            import google.generativeai as genai
            response = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_query"
            )
            return response['embedding']

embedding_service = EmbeddingService()
