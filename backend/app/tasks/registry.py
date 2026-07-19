"""
Background Task Definitions.
Phase 1 uses a simple in-process task registry.
Replace with Celery or ARQ workers in Phase 9 (Production).
"""
from __future__ import annotations

import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

_task_registry: dict[str, Callable] = {}


def background_task(name: str):
    """Decorator to register a function as a background task."""
    def decorator(func: Callable) -> Callable:
        _task_registry[name] = func
        logger.debug(f"Registered background task: {name}")
        return func
    return decorator


def get_task(name: str) -> Callable | None:
    return _task_registry.get(name)
