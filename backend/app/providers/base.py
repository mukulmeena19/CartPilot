"""
Abstract Provider Interfaces.
Every external dependency must be accessed through these contracts.
No business service should directly import a vendor SDK.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Tuple
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    """Contract for all language model integrations."""

    @abstractmethod
    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
    ) -> Tuple[T, Dict[str, Any]]:
        """
        Call the LLM and parse the response into a Pydantic model.
        Returns the parsed model and metadata (tokens, latency, model_name).
        """


class EmbeddingProvider(ABC):
    """Contract for all text embedding integrations."""

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Return a list of embedding vectors for the given texts."""


class CacheProvider(ABC):
    """Contract for caching backends (in-memory, Redis, etc.)."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a cached value. Returns None on miss."""

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Store a value with an optional TTL."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove a cached value."""

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check whether a key exists in the cache."""


class StorageProvider(ABC):
    """Contract for file/blob storage backends."""

    @abstractmethod
    async def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Upload bytes and return a public/pre-signed URL."""

    @abstractmethod
    async def download(self, key: str) -> bytes:
        """Download and return file bytes by key."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a stored object by key."""


class NotificationProvider(ABC):
    """Contract for push/email/SMS notification backends."""

    @abstractmethod
    async def send(self, recipient: str, subject: str, body: str) -> None:
        """Send a notification to a recipient."""
