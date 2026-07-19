import json
import uuid
from typing import Dict, Any, Type, TypeVar, Tuple
from pydantic import BaseModel

from app.ai.providers.base import LLMProvider

T = TypeVar('T', bound=BaseModel)

class MockProvider(LLMProvider):
    """
    A deterministic Mock LLM Provider for testing without API keys.
    Returns realistic mock shopping cart data for any query.
    """
    
    def generate_structured(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        response_model: Type[T]
    ) -> Tuple[T, Dict[str, Any]]:
        
        schema_name = response_model.__name__
        
        if schema_name == "GoalContext":
            mock_data = {
                "goal_type": "weekly_groceries",
                "shopping_goal": "Weekly grocery shopping",
                "people": 2,
                "budget": 2500.0,
                "duration": "7 days",
                "dietary_preferences": ["vegetarian"],
                "brand_preferences": [],
                "constraints": [],
                "confidence": 0.92
            }
        elif schema_name == "AIPlanningInference":
            mock_data = {
                "categories": [
                    {
                        "name": "Dairy & Protein",
                        "weight": 8.0,
                        "target_quantity": "high",
                        "reasoning": "Essential for vegetarian protein intake."
                    },
                    {
                        "name": "Fresh Vegetables",
                        "weight": 7.0,
                        "target_quantity": "high",
                        "reasoning": "Core of a vegetarian diet."
                    },
                    {
                        "name": "Grains & Staples",
                        "weight": 6.0,
                        "target_quantity": "medium",
                        "reasoning": "Provides carbohydrates and energy."
                    }
                ],
                "confidence": 0.90
            }
        elif schema_name == "ShoppingPlan":
            mock_data = {
                "categories": [
                    {
                        "name": "Dairy & Protein",
                        "priority": 1,
                        "estimated_budget": 800.0,
                        "target_quantity": "high",
                        "reasoning": "Milk, paneer, curd for protein."
                    },
                    {
                        "name": "Fresh Vegetables",
                        "priority": 2,
                        "estimated_budget": 1000.0,
                        "target_quantity": "high",
                        "reasoning": "Tomatoes, onions, greens."
                    },
                    {
                        "name": "Grains & Staples",
                        "priority": 3,
                        "estimated_budget": 700.0,
                        "target_quantity": "medium",
                        "reasoning": "Rice, dal, atta."
                    }
                ],
                "total_budget": 2500.0,
                "goal_confidence": 0.92,
                "planning_confidence": 0.90,
                "assumptions": ["Budget in INR based on common usage."]
            }
        else:
            # Generic fallback - try to build a minimal valid response
            raise ValueError(f"MockProvider has no predefined response for schema: {schema_name}")
        
        return response_model.model_validate(mock_data), {"model": "mock", "tokens": 0, "latency": 0.01}
