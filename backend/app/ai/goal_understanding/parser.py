from app.ai.providers.base import LLMProvider
from app.ai.prompts.goal_understanding_v1 import GOAL_UNDERSTANDING_SYSTEM_PROMPT_V1
from app.ai.goal_understanding.models import GoalContext
from typing import Tuple, Dict, Any

class GoalParser:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def parse_query(self, user_query: str) -> Tuple[GoalContext, Dict[str, Any]]:
        """
        Takes a natural language query, passes it to the LLM Provider with the V1 prompt,
        and returns the structured GoalContext alongside observability metadata.
        """
        system_prompt = GOAL_UNDERSTANDING_SYSTEM_PROMPT_V1
        
        goal_context, metadata = self.provider.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_query,
            response_model=GoalContext
        )
        
        return goal_context, metadata
