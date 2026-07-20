import sys
import asyncio
from app.services.conversation_manager import ConversationManager
from app.db.session import SessionLocal
from app.db.models import user, product, category, cart, order, inventory, token, intelligence, knowledge, restaurant, analytics

async def main():
    db = SessionLocal()
    manager = ConversationManager(db)
    
    print("--- STARTING SSE STREAM ---")
    try:
        async for event in manager.process_conversation("biryani under 300 rupees near me", 1):
            print(f"event: {event.event}")
            print(f"data: {event.data}")
            print("---")
    finally:
        db.close()
    print("--- END OF SSE STREAM ---")

if __name__ == "__main__":
    asyncio.run(main())
