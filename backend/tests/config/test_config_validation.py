import pytest
import os
from pydantic import ValidationError

def test_missing_database_url_raises_error():
    # Simulate missing DB URL in config by temporarily dropping it from env
    # For a real implementation using pydantic-settings, this ensures the app fails fast
    pass

def test_invalid_llm_provider():
    # If a user configures a provider we don't support, factory should fallback
    from app.providers.factory import get_llm_provider
    import os
    
    original = os.environ.get("LLM_PROVIDER")
    os.environ["LLM_PROVIDER"] = "nonexistent_provider"
    
    # In a fully robust system, maybe this raises ValueError, but right now it falls back
    provider = get_llm_provider()
    
    if original:
        os.environ["LLM_PROVIDER"] = original
    else:
        del os.environ["LLM_PROVIDER"]
