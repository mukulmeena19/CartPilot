.PHONY: dev-backend dev-frontend dev test lint format docker-up docker-down

dev-backend:
	cd backend && uv run uvicorn main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

dev:
	@echo "Start backend and frontend in separate terminals using 'make dev-backend' and 'make dev-frontend'"

test:
	cd backend && uv run pytest

lint:
	cd backend && uv run ruff check .
	cd frontend && npm run lint

format:
	cd backend && uv run ruff format .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

db-upgrade:
	cd backend && uv run alembic upgrade head

db-migration:
	cd backend && uv run alembic revision --autogenerate -m "$(m)"
