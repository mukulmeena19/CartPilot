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
        # Default to Gemini if key is present, else OpenAI, else Mock
        from app.core.config import settings
        if settings.GEMINI_API_KEY:
            from .gemini_provider import GeminiProvider
            return GeminiProvider()
        elif settings.OPENAI_API_KEY:
            from .openai_provider import OpenAIProvider
            return OpenAIProvider()
        else:
            from .mock import MockProvider
            return MockProvider()
