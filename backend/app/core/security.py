import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
import bcrypt
from app.core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Short lived access token (15 minutes)
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token() -> str:
    # 32 bytes of secure random hex string
    return secrets.token_hex(32)

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class PromptSecurity:
    """
    Lightweight heuristic-based prompt injection safeguard.
    """
    
    # Common jailbreak patterns
    JAILBREAK_PATTERNS = [
        r"(?i)ignore previous instructions",
        r"(?i)disregard previous instructions",
        r"(?i)you are now",
        r"(?i)system prompt",
        r"(?i)print your instructions",
        r"(?i)developer mode",
        r"(?i)act as a",
        r"(?i)DAN",  # Do Anything Now
    ]
    
    _compiled_patterns = [re.compile(p) for p in JAILBREAK_PATTERNS]

    @classmethod
    def scan_input(cls, user_input: str) -> Tuple[bool, str]:
        """
        Scans user input for potential prompt injection patterns.
        Returns a tuple: (is_safe: bool, reason: str)
        """
        if not user_input:
            return True, ""
            
        for pattern in cls._compiled_patterns:
            if pattern.search(user_input):
                logger.warning(f"Blocked potential prompt injection. Matched pattern: {pattern.pattern}")
                return False, "Input flagged by security filters."
                
        return True, ""
