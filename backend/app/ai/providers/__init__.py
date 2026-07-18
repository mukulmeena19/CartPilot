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
        # Default to OpenAI
        from .openai_provider import OpenAIProvider
        return OpenAIProvider()
