import time
import json
from typing import TypeVar, Type, Dict, Any, Tuple
from pydantic import BaseModel
from google import genai
from google.genai import types

from .base import LLMProvider
from app.core.config import settings

T = TypeVar('T', bound=BaseModel)

class GeminiProvider(LLMProvider):
    def __init__(self):
        # Initialize the client. It will automatically pick up GEMINI_API_KEY from environment 
        # or it can be explicitly passed.
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-2.5-flash"

    def generate_structured(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        response_model: Type[T]
    ) -> Tuple[T, Dict[str, Any]]:
        
        start_time = time.time()
        
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=response_model,
            temperature=0.0
        )
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=config,
        )
        
        latency = time.time() - start_time
        
        # Parse the JSON string back into the Pydantic model
        parsed_data = json.loads(response.text)
        result_instance = response_model.model_validate(parsed_data)
        
        metadata = {
            "latency": latency,
            "provider": "gemini",
            "model": self.model_name
        }
        
        return result_instance, metadata
