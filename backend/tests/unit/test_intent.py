import pytest
from app.workflows.intent import IntentResolver, IntentClassification

# We can mock the LLM Provider for unit tests to ensure our structured parsing is robust
class MockLLMProvider:
    def generate_structured(self, system_prompt, user_prompt, response_model):
        if "order food" in user_prompt.lower():
            return IntentClassification(
                intent_type="new_request",
                confidence=0.9,
                domain="food_ordering",
                extracted_entities={"intent": "food"},
                needs_clarification=False,
                clarification_question=None
            ), {}
        elif "confusing" in user_prompt.lower():
            return IntentClassification(
                intent_type="follow_up",
                confidence=0.4,
                domain=None,
                extracted_entities={},
                needs_clarification=True,
                clarification_question="Could you clarify what you meant?"
            ), {}
        
        return IntentClassification(
            intent_type="general_question",
            confidence=0.8,
            domain=None,
            extracted_entities={},
            needs_clarification=False,
            clarification_question=None
        ), {}

@pytest.mark.asyncio
async def test_intent_resolution():
    resolver = IntentResolver()
    resolver.llm = MockLLMProvider()
    
    # 1. Clear intent
    result = await resolver.resolve("session-1", "", "I want to order food.")
    assert result.domain == "food_ordering"
    assert result.intent_type == "new_request"
    assert not result.needs_clarification
    
    # 2. Confusing intent
    result2 = await resolver.resolve("session-1", "", "This is confusing")
    assert result2.needs_clarification
    assert result2.clarification_question == "Could you clarify what you meant?"
