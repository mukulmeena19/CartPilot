import json
import uuid
from typing import Dict, Any, Type, TypeVar
from pydantic import BaseModel

from app.ai.providers.base import LLMProvider
from app.ai.understanding.models import GoalContext
from app.ai.planning.models import ShoppingPlan, CategoryAllocation

T = TypeVar('T', bound=BaseModel)

class MockProvider(LLMProvider):
    """
    A deterministic Mock LLM Provider for End-to-End automated testing.
    It completely bypasses network calls to guarantee fast, reliable tests.
    """
    
    def generate_structured_response(self, prompt: str, schema: Type[T]) -> T:
        """
        Interrogates the schema requested and returns a deterministic mock payload.
        """
        
        if schema == GoalContext:
            # Deterministic response for Goal Understanding
            mock_data = {
                "goal_type": "meal_prep",
                "people": 2,
                "budget": 2500,
                "duration": "7 days",
                "dietary_preferences": ["vegetarian", "high_protein"],
                "meal_types": ["breakfast", "dinner"],
                "excluded_ingredients": [],
                "confidence_score": 0.95,
                "missing_information": [],
                "assumptions": ["Assuming Indian currency (₹) based on common threshold 2500."]
            }
            return schema.model_validate(mock_data)
            
        elif schema == ShoppingPlan:
            # Deterministic response for Shopping Plan
            mock_data = {
                "categories": [
                    {
                        "name": "Dairy",
                        "priority": 1,
                        "estimated_budget": 1000.0,
                        "target_quantity": "high",
                        "reasoning": "High protein requirement necessitates dairy (milk, paneer)."
                    },
                    {
                        "name": "Vegetables",
                        "priority": 2,
                        "estimated_budget": 1500.0,
                        "target_quantity": "medium",
                        "reasoning": "Vegetarian diet requires fresh produce."
                    }
                ],
                "total_budget": 2500.0,
                "goal_confidence": 0.9,
                "planning_confidence": 0.95,
                "assumptions": ["Budget splits safely without hitting the exact 2500 ceiling."]
            }
            return schema.model_validate(mock_data)
            
        else:
            raise ValueError(f"MockProvider does not have a predefined response for schema {schema.__name__}")
