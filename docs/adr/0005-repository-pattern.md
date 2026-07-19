# ADR 0005: Repository Pattern for Data Access

## Problem
In early iterations, FastAPI route handlers directly imported SQLAlchemy sessions and executed complex queries (e.g., querying users, items, parsing relationships). This tightly coupled our HTTP presentation layer to our specific ORM and database technology, making unit testing difficult (requiring a live test DB) and code reuse poor.

## Alternatives Considered
- Active Record (e.g., Django ORM style, putting `save()` methods on models).
- Raw SQL queries encapsulated in functions.
- The Repository Pattern.

## Solution
We adopted the Repository Pattern. We created abstract repository classes (or concrete classes that inject `Session`) located in `app/db/repositories/`. Every entity (User, Product, Order, RecommendationLog) has a dedicated repository responsible for all database interactions. Services and Routers never call `db.query()` directly; they call methods like `product_repo.get_by_id()`.

## Why
This provides several key benefits:
1. **Separation of Concerns**: Business logic doesn't care if we use PostgreSQL, MongoDB, or an in-memory dictionary.
2. **Testability**: We can easily mock the repository interfaces in unit tests without standing up a database.
3. **Reusability**: Complex queries (like fetching a cart with all relationships) are written once in the repository and reused across multiple services.
