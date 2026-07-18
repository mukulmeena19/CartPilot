from abc import ABC, abstractmethod
from typing import TypeVar, Type, Dict, Any, Tuple
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers (OpenAI, Anthropic, Gemini, etc.).
    Ensures that business logic remains vendor-agnostic.
    """
    
    @abstractmethod
    def generate_structured(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        response_model: Type[T]
    ) -> Tuple[T, Dict[str, Any]]:
        """
        Executes an LLM request enforcing a structured JSON output based on the provided Pydantic model.
        
        Args:
            system_prompt (str): The system instructions.
            user_prompt (str): The user input/query.
            response_model (Type[T]): The Pydantic model class to validate and return.
            
        Returns:
            Tuple[T, Dict[str, Any]]: 
                - The parsed and validated Pydantic model instance.
                - Observability metadata (e.g., prompt_tokens, completion_tokens, latency, model_name).
        """
        pass
