from abc import ABC, abstractmethod
from typing import List
from app.core.config import settings

class EmbeddingProvider(ABC):
    @abstractmethod
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        pass

class MockEmbeddingProvider(EmbeddingProvider):
    """Returns zero vectors - used when no embedding API key is configured."""
    def __init__(self, dimensions: int = 1536):
        self.dimensions = dimensions

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [[0.0] * self.dimensions for _ in texts]

class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "text-embedding-3-small"):
        from openai import OpenAI
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model_name = model_name

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates 1536-dimensional embeddings for a list of texts using OpenAI.
        """
        if not texts:
            return []
            
        # Clean texts
        cleaned_texts = [text.replace("\n", " ") for text in texts]
        
        response = self.client.embeddings.create(
            input=cleaned_texts,
            model=self.model_name
        )
        
        # Sort by index to ensure returned embeddings match the order of input texts
        sorted_data = sorted(response.data, key=lambda x: x.index)
        return [item.embedding for item in sorted_data]

def get_embedding_provider() -> EmbeddingProvider:
    """Returns the best available embedding provider."""
    if settings.OPENAI_API_KEY:
        return OpenAIEmbeddingProvider()
    return MockEmbeddingProvider()
