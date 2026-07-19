# ADR 0001: Clean Architecture for Backend

## Problem
The backend needed a structure that separates concerns, remains scalable, and keeps AI integration logic distinct from business logic.

## Alternatives Considered
- Standard MVC (Model-View-Controller)
- Microservices
- Clean Architecture / Domain-Driven Design (DDD)

## Solution
We adopted a flavor of Clean Architecture, organizing the code into distinct layers:
- `app/api/`: Presentation layer (FastAPI routers).
- `app/services/`: Business logic and orchestrators.
- `app/engine/`: AI and recommendation specific domain logic.
- `app/db/`: Data access layer (Repositories and SQLAlchemy models).
- `app/schemas/`: Data transfer objects (Pydantic).

## Why
This structure prevents the AI logic (which relies on embeddings and complex pipelines) from bleeding into the standard e-commerce CRUD operations. It makes the system testable, scalable, and easy to navigate for new engineers joining the team.
