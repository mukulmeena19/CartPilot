import time
import json
from typing import TypeVar, Type, Dict, Any, Tuple
from pydantic import BaseModel
from openai import OpenAI
from app.core.config import settings
from app.ai.providers.base import LLMProvider
from app.ai.exceptions import InvalidLLMResponseError

T = TypeVar('T', bound=BaseModel)

class OpenAIProvider(LLMProvider):
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model_name = model_name

    def generate_structured(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        response_model: Type[T]
    ) -> Tuple[T, Dict[str, Any]]:
        start_time = time.time()
        
        try:
            # Using OpenAI Structured Outputs (beta feature or parse feature via sdk)
            # In latest openai >= 1.35.0, client.beta.chat.completions.parse is available
            response = self.client.beta.chat.completions.parse(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=response_model
            )
            
            message = response.choices[0].message
            if message.parsed:
                parsed_obj = message.parsed
            elif message.content:
                # Fallback if parsed isn't explicitly set but content is JSON
                parsed_obj = response_model.model_validate_json(message.content)
            else:
                raise InvalidLLMResponseError("OpenAI returned an empty response.")
                
            latency = time.time() - start_time
            
            usage = response.usage
            metadata = {
                "model": self.model_name,
                "latency_sec": latency,
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
                "total_tokens": usage.total_tokens if usage else 0,
            }
            
            return parsed_obj, metadata
            
        except Exception as e:
            raise InvalidLLMResponseError(f"Failed to generate structured response from OpenAI: {str(e)}")
