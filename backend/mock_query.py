from app.ai.providers import get_llm_provider

def run_mock_query():
    provider = get_llm_provider()
    items_context = [
        "- Chicken Dum Biryani (Spicy Kitchen) (Rs. 250.00): Fits your budget of Rs. 300 and has a high rating.",
        "- Veg Hyderabadi Biryani (Authentic Indian Bistro) (Rs. 220.00): Great vegetarian option within your budget."
    ]
    prompt = (
        "You are a helpful AI shopping assistant. Write a short, natural language summary (1-2 sentences) "
        "about the following cart items you selected for the user. Do not invent any discounts, prices, or products "
        "that are not listed below. Do not use markdown.\n\n"
        f"Selected Items:\n{chr(10).join(items_context)}"
    )

    print("\n--- RESULTS FOR: 'biryani under 300 rupees near me' ---")
    print("Items Returned:")
    for item in items_context:
        print(item)
        
    print("\nPrompting LLM with...")
    print(prompt)

    try:
        llm_response = provider.generate(
            prompt=prompt,
            system_prompt="You are a concise shopping assistant.",
            temperature=0.3,
        )
        if isinstance(llm_response, dict) and "text" in llm_response:
            summary = llm_response["text"].strip()
        elif hasattr(llm_response, "text"):
            summary = llm_response.text.strip()
        else:
            summary = str(llm_response).strip()
            
        print("\nGenerated Cart Summary:")
        print(summary)
    except Exception as e:
        print("\nFailed to generate summary:", e)

if __name__ == "__main__":
    run_mock_query()
