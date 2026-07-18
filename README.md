# CartPilot 🛒

CartPilot is an advanced, production-ready AI Shopping Assistant that translates natural language goals into fully optimized, budget-constrained, and explainable grocery carts.

## Architecture

CartPilot strictly enforces a decoupled architecture:
- **Frontend (Presentation Only)**: A premium Next.js/React streaming interface powered by Tailwind and Zustand. The frontend *never* holds business logic or internal pipeline states.
- **Backend (Orchestrator)**: A powerful 7-stage deterministic AI pipeline written in Python (FastAPI).

### The 7-Stage AI Pipeline
1. **Goal Understanding**: Parses user intent using an LLM to extract budgets, dietary requirements, and missing info.
2. **Planning**: Allocates budget dynamically across categories based on the parsed goal.
3. **Retrieval**: Uses `pgvector` to semantically search a PostgreSQL database for candidate products.
4. **Verification**: A strict deterministic engine that checks stock availability and price thresholds.
5. **Memory**: Injects historical user preferences (liked brands, allergies).
6. **Optimization**: Solves a multi-constraint Knapsack-like problem to maximize value within the budget.
7. **Explainability**: Deterministically generates human-readable reasoning for every single product selected.

## Technology Stack
- **Frontend**: Next.js (App Router), React, TypeScript, Tailwind CSS, Shadcn UI, Zustand.
- **Backend**: Python 3.12, FastAPI, SQLAlchemy, Pydantic.
- **AI Integration**: OpenAI / Gemini via a custom Provider Factory.

## Multi-Cloud Deployment (Vercel + Railway + Supabase)

This is the recommended architecture for a highly scalable, edge-cached production deployment. Because Vercel and Railway hook directly into GitHub, you **do not** need to manually build Docker containers on your local machine.

### 1. Database (Supabase)
1. Create a new project on [Supabase](https://supabase.com/).
2. Navigate to the SQL Editor and run `CREATE EXTENSION IF NOT EXISTS vector;`.
3. Get your connection string (Session pooling URL) from Database Settings.
4. Locally, set `DATABASE_URL` to your Supabase URL and run the migrations:
   ```bash
   cd backend
   alembic upgrade head
   python scripts/seed_catalog.py --size 1000
   ```

### 2. Backend (Railway)
The repository includes a `railway.json` configuration file.
1. Connect your GitHub repository to [Railway](https://railway.app/).
2. Railway will automatically detect the `railway.json` file and build the `backend/Dockerfile`.
3. In the Railway Variables tab, add your `DATABASE_URL` and `OPENAI_API_KEY`.
4. Railway will provide a public URL (e.g., `https://cartpilot-backend.up.railway.app`). Copy this URL.

### 3. Frontend (Vercel)
The repository includes a `vercel.json` configuration file.
1. Connect your GitHub repository to [Vercel](https://vercel.com/).
2. Vercel will automatically detect `vercel.json` and build the Next.js frontend.
3. In the Vercel Environment Variables settings, add:
   - `NEXT_PUBLIC_API_URL`: Set this to your Railway URL.
4. Deploy! Your fully scalable, multi-cloud CartPilot is now live.

---

## Docker Deployment (Local / VPS)

CartPilot is fully containerized and can be deployed anywhere using Docker Compose.

### Prerequisites
- Docker
- Docker Compose

### Development Environment
To run the full stack locally with hot-reloading (mounted volumes):
```bash
# 1. Copy the environment file
cp .env.example .env

# 2. Start the development cluster
docker compose -f docker/compose.dev.yml up --build

# The UI will be available at http://localhost:3000
# The API will be available at http://localhost:8000
```

### Production Environment
To deploy a hardened, production-ready stack (no mounted volumes, multi-stage Next.js standalone build):
```bash
docker compose -f docker/compose.prod.yml up -d --build
```

### Useful Docker Commands
```bash
# View logs
docker compose -f docker/compose.prod.yml logs -f

# Stop containers
docker compose -f docker/compose.prod.yml down

# Seed the database manually if needed
docker exec -it cartpilot-backend-prod python scripts/seed_catalog.py --size 100
```

## Local Setup (Without Docker)

### Backend Setup
```bash
cd backend
# Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run database migrations
alembic upgrade head

# Seed the database
python scripts/seed_catalog.py --size 100

# Run the backend
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

### Backend (`backend/.env`)
| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (e.g. `postgresql://user:pass@localhost:5432/cartpilot`) |
| `LLM_PROVIDER` | `openai`, `gemini`, or `mock` for local deterministic testing. |
| `OPENAI_API_KEY` | Your OpenAI API key (if using OpenAI). |

### Frontend (`frontend/.env.local`)
| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | URL of the backend (e.g. `http://localhost:8000`) |

## Running Tests

CartPilot includes a deterministic End-to-End pipeline testing script that verifies the orchestrator emits the correct Server-Sent Events (SSE) and handles errors gracefully.

```bash
# Set provider to mock to run deterministically without internet
export LLM_PROVIDER=mock
python scripts/test_e2e_pipeline.py
```

## Observability & Health
- `GET /health` - Basic health check.
- `GET /ready` - Deep readiness check that validates DB connectivity, `pgvector`, and LLM Provider configuration.
- The pipeline utilizes `structlog` to emit structured JSON logs capturing latency, tokens, and verification stats for every stage.
