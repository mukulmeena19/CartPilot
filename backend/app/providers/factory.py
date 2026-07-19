"""
Provider factory.
Returns the best available implementation for each provider type.
Business logic must only use these factory functions, never concrete providers directly.
"""
from __future__ import annotations

import os
from functools import lru_cache

from app.providers.base import CacheProvider, EmbeddingProvider, LLMProvider


@lru_cache(maxsize=1)
def get_llm_provider() -> LLMProvider:
    """Return the configured LLM provider."""
    provider_name = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider_name == "gemini":
        from app.ai.providers.gemini_provider import GeminiProvider
        return GeminiProvider()

    if provider_name == "openai":
        from app.ai.providers.openai_provider import OpenAIProvider
        return OpenAIProvider()

    # Fallback: auto-detect from available keys
    if os.environ.get("GEMINI_API_KEY"):
        from app.ai.providers.gemini_provider import GeminiProvider
        return GeminiProvider()

    if os.environ.get("OPENAI_API_KEY"):
        from app.ai.providers.openai_provider import OpenAIProvider
        return OpenAIProvider()

    from app.ai.providers.mock import MockProvider
    return MockProvider()


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    """Return the configured Embedding provider."""
    if os.environ.get("OPENAI_API_KEY"):
        from app.ai.providers.embeddings import OpenAIEmbeddingProvider
        return OpenAIEmbeddingProvider()

    from app.ai.providers.embeddings import MockEmbeddingProvider
    return MockEmbeddingProvider()


@lru_cache(maxsize=1)
def get_cache_provider() -> CacheProvider:
    """Return the configured Cache provider."""
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        # TODO (Phase 1): Implement RedisCacheProvider
        pass

    from app.providers.cache import InMemoryCacheProvider
    return InMemoryCacheProvider()
