# CartPilot 🛒

CartPilot is an advanced, production-ready AI Shopping Assistant that translates natural language goals into fully optimized, budget-constrained, and explainable carts across multiple domains (Grocery & Restaurants).

## What We Built

CartPilot scales beyond a simple AI wrapper into a full-stack, autonomous concierge:
- **Multi-Agent Orchestrator**: Intelligently routes user intents to domain-specific workflows (e.g., Grocery vs. Food Delivery).
- **Massive Real-World Dataset**: Seeded with **57,000+ real BigBasket products** and **15,000+ Zomato restaurants** across India, moving away from synthetic mock data.
- **Hybrid Retrieval on PostgreSQL**: Uses `pgvector` for semantic search combined with strict relational filtering (price, category, availability) to eliminate LLM hallucinations.
- **Local Cost-Free Embeddings**: Integrates `sentence-transformers` (`all-MiniLM-L6-v2`) to embed 72,000+ items locally, entirely bypassing API embedding costs.
- **Dynamic User Memory**: Autonomously extracts and remembers dietary preferences, brand affinities, and price sensitivities to hyper-personalize future requests.
- **Streaming UI**: A premium Next.js frontend with Framer Motion that consumes Server-Sent Events (SSE) to stream the agent's thoughts and results in real-time.

## Technology Stack
- **Frontend**: Next.js (App Router), React, TypeScript, Tailwind CSS, Lucide React, Framer Motion, Zustand.
- **Backend**: Python 3.12, FastAPI, SQLAlchemy, Pydantic, Server-Sent Events (SSE).
- **Database**: PostgreSQL with `pgvector`.
- **AI/ML**: Gemini API (Google GenAI) for orchestration & reasoning, `sentence-transformers` for local vector generation.

## Local Setup

### 1. Database Setup
Ensure you have PostgreSQL running with the `pgvector` extension installed.
```bash
# Create database and extension
createdb cartpilot_db
psql -d cartpilot_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 2. Backend Setup
```bash
cd backend
# Install dependencies using uv
uv sync
# Or manually install with pip if not using uv

# Set up environment variables
cp .env.example .env
# Make sure to add your GEMINI_API_KEY in .env

# Run the backend
uv run uvicorn main:app --reload
```

### 3. Data Seeding (Real Datasets)
CartPilot comes with automated scripts to seed the massive datasets. These scripts use local sentence-transformers to avoid API costs.
```bash
cd backend
# 1. Seed Zomato Restaurants
uv run python scripts/seed_zomato_restaurants.py

# 2. Seed BigBasket Grocery Catalog (Generates 5,000 embeddings locally)
uv run python scripts/seed_bigbasket.py

# 3. Generate AI Menus for Zomato (Uses Gemini to hallucinate realistic menus based on budget)
uv run python scripts/generate_menu_items.py
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
# The UI will be available at http://localhost:3000
```

## Architecture

CartPilot strictly enforces a decoupled architecture:
- **Frontend (Presentation Only)**: A premium Next.js/React streaming interface. The frontend *never* holds business logic or internal pipeline states.
- **Backend (Orchestrator)**: A powerful multi-stage deterministic AI pipeline written in Python (FastAPI).

### The 7-Stage AI Pipeline
1. **Goal Understanding & Routing**: Parses user intent using Gemini to extract budgets, dietary requirements, and route to the correct domain (Grocery vs. Food).
2. **Memory Injection**: Injects historical user preferences (liked brands, allergies) into the context window.
3. **Planning**: Allocates budget dynamically across categories based on the parsed goal.
4. **Retrieval**: Uses `pgvector` and `sentence-transformers` to semantically search PostgreSQL for candidate products/restaurants.
5. **Verification**: A strict deterministic engine that checks stock availability and price thresholds.
6. **Optimization**: Solves a multi-constraint problem to maximize value within the budget.
7. **Streaming & Explainability**: Streams back reasoning for every single product selected via SSE.
