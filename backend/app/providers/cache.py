"""
In-memory cache provider.
Suitable for development and single-process deployments.
Replace with RedisCacheProvider for production.
"""
from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, Optional, Tuple

from app.providers.base import CacheProvider


class InMemoryCacheProvider(CacheProvider):
    """
    Thread-safe in-memory cache using a simple dict with TTL tracking.
    Designed to be a drop-in replacement for Redis during local development.
    """

    def __init__(self) -> None:
        # Stores (value, expiry_timestamp). expiry_timestamp = 0 means no expiry.
        self._store: Dict[str, Tuple[Any, float]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expiry = entry
            if expiry and time.monotonic() > expiry:
                del self._store[key]
                return None
            return value

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        expiry = time.monotonic() + ttl_seconds if ttl_seconds else 0.0
        async with self._lock:
            self._store[key] = (value, expiry)

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._store.pop(key, None)

    async def exists(self, key: str) -> bool:
        return await self.get(key) is not None
