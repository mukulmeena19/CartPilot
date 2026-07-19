import logging
import structlog
import uuid
from typing import Any, MutableMapping
from fastapi import Request

# Fields to redact for security
SENSITIVE_KEYS = {"password", "token", "access_token", "refresh_token", "secret", "authorization"}

def redact_sensitive_data(logger: logging.Logger, name: str, event_dict: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    for key, value in event_dict.items():
        if any(sensitive in key.lower() for sensitive in SENSITIVE_KEYS):
            event_dict[key] = "[REDACTED]"
    return event_dict

def setup_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            redact_sensitive_data,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
    )

def get_logger(name: str) -> structlog.BoundLogger:
    return structlog.get_logger(name)
