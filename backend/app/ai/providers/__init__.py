import os
from .base import LLMProvider

def get_llm_provider() -> LLMProvider:
    provider_name = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider_name == "mock":
        from .mock import MockProvider
        return MockProvider()
    elif provider_name == "gemini":
        from .gemini import GeminiProvider # Hypothetical future provider
        return GeminiProvider()
    else:
        # Default to OpenAI if key is present, else fallback to Mock
        from app.core.config import settings
        if not settings.OPENAI_API_KEY:
            from .mock import MockProvider
            return MockProvider()
        else:
            from .openai_provider import OpenAIProvider
            return OpenAIProvider()
