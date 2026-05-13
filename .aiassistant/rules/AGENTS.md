---
apply: always
---

# FastAPI Guidelines

You are an expert in Python, FastAPI, and scalable async web application development. 
You write secure, maintainable, and performant code following FastAPI and Python best practices.

## General
- Do not commit to Git without consent from me.
- Do not perform more tasks than are outlined in the prompt.
- Ask clarifying questions if you need more context. Prompts written by me can and might not be fully detailed for 
you to perform the best work.
- All changes must be roll-backable (never introduce irrevertible changes).
- Do not write tests or run tests unless you are asked to.

## Python Best Practices
- Follow PEP 8 with a 120-character line limit.
- Use double quotes for Python strings.
- Sort imports with `isort`, code formatting with `black`.
- Use f-strings for string formatting.
- Use type hints everywhere — parameters, return types, and class attributes.

## Async First Approach
- Use async-first design — prefer `async def` routes for all I/O-bound operations. If it can be awaited, await it.
- Never call blocking operations (e.g. `time.sleep`, sync DB calls) inside `async` routes; use `await` equivalents 
or offload to a threadpool. 
- Use `asyncer` library to smoothly call sync code as async (`asyncer.asyncify`), or async as sync (`asyncer.syncify`)

## FastAPI Best Practices
- Use Pydantic excessively, if it is any form of input validation, output serialization, and settings management.
- Use dependency injection via `Depends()` for shared logic — do not repeat auth, DB session, or permission checks inline in routes
- Prefer FastAPI's built-in features (dependencies, response models, status codes) before reaching for third-party packages

## Global Project Structure
- Follow a domain-driven layout, grouping files by feature module rather than file type
- `src/main.py` is the app entry point; keep it thin — only app initialization and router registration
- Global shared concerns (database session, pagination, base exceptions, global config) live directly in `src/`.
- When importing across modules, use explicit module-level imports to avoid circular dependencies.

## Per Domain Project Structure
- Each module lives in its own directory under `src/` and contains: `router.py`, `schemas.py`, `models.py`, 
`dependencies.py`, `exceptions.py` — include only what the module needs.
- Each module builds its own service package `/src/<domain>/service` with using `__init__.py` to define the public API
that the outer caller per domain (e.g. `router.py`, `dependencies.py`) will need.

## Schemas (Pydantic)
- Never return raw ORM objects from routes — always serialize through a response schema with `response_model`
- Never trust any external inputs from users, or third party clients. Always validate them with Pydantic before using it
in our app's ecosystem.
- Define separate schemas for request input, response output, and DB representation — never reuse the same schema for different purposes.
- Use a shared `CustomBaseModel` to enforce project-wide conventions (e.g. `alias_generator`, `populate_by_name`)
- Use `model_validator` and `field_validator` for cross-field validation logic instead of putting it in routes or services.
- Pydantic can even be used as a parser class.

## Routes
- Keep route functions thin — delegate all business logic to `/service`.
- Always set explicit `response_model`, `status_code`, `summary`, and `descriptions` on route decorators
- Validate and document all possible response codes using the `responses` parameter for OpenAPI accuracy
- Use `HTTPException` with explicit status codes; never let unhandled exceptions surface to the client
- If a route has a clear `response_model`, let its return value implicit ride upstream to form the response_model instead
of explicitly crafting one below (e.g., `return await create_user` -> `ORM-users` -> `UserResponse`)

## Dependencies
- All non-query `Depends()` call from `router.py` lives here (query `Depends()` pull from `schemas.py`)
- Anything related to lifecycle management (e.g., `get_redis`), auth/authz (e.g., `valid_current_user`, `require_role`), 
feature flags (`require_feature`), rate limiting (e.g. `rate_limit`), or in general anything that requires request context
to function (e.g., `get_request_context`)
- Use dependency chaining to build layered authorization or context (e.g. `get_current_user` → `require_role("admin")`)
- `async` dependencies for anything that can be awaited, e.g., touches the database or external services.

## Service Package
- All modules inside `/service` contain only business logic — no FastAPI imports, no `Request`, no `Depends`.
- Each domain's `/service` package determines what module it needs for varying level of business logics. In general, 
if working with third-party, use `client.py`. If working with db -> `crud.py`, etc. 
- The `/service` package can contain a `flow.py` to act as the premier primary logic orchestrator that `router.py` can
call from if the logic is multi-modules (requires different modules to work together instead of just simple CRUD)
- Outer callers never call individual modules inside the `/service` package (e.g., never 
`from src.google.service.client import ...` inside `router.py`)
- Modules inside `/service` are the only one who should import and use domain settings from `settings.py`.
- Keep services independently testable without needing to spin up the full app.

## Exceptions
- Define module-specific exceptions in `exceptions.py` (e.g. `PostNotFound`, `InvalidCredentials`)
- Register global exception handlers in `main.py` to convert domain exceptions to `HTTPException` responses
- Never raise `HTTPException` anywhere else other than here. Other modules should only ever know about its domain exceptions.

## Models (SQLAlchemy)
- Define all SQLAlchemy models in the module's `models.py` with explicit column types and constraints.
- Use `relationship` to define ORM foreign relatinoships.
- Column naming should be snake_case singular form(e.g. `name`, `email`, `like_post_id`, etc.)
- Use `__tablename__` in snake_case plural form (e.g. `posts`, `user_profiles`)
- Use `_time` suffix for datetime columns and `_date` suffix for date columns
- Always define indexes explicitly and follow a consistent naming convention via SQLAlchemy `MetaData`

## Database
- Use Alembic for all schema migrations — never mutate the DB schema manually.
- Take into account the fact that our app uses an async driver, while Alembic is sync first.
- Take into account the fact that we use SQLite for testing, but PostgreSQL in productions, so certain conventions might
not apply fully between the two (e.g., SQLite needs batch_op for altering column.)
- Write migrations that are static and reversible; use the `date_slug` file template (e.g. `2024-08-24_add_post_index.py`)
- Use `select_related` patterns (SQLAlchemy `joinedload` / explicit joins) to avoid N+1 query problems
- Prefer doing complex joins and aggregations in SQL rather than in Python
- Never use raw SQL strings unless absolutely necessary and always parameterize inputs if you do

## Settings & Configuration
- Manage all global all configuration through a Pydantic `BaseSettings` class in `src/config.py`, while domain settings
inherit from `DomainSettings` and provide configuration for their respective domain.
- Load values from environment variables; never hardcode secrets or environment-specific values.
- Never commit `.env` files or secrets to version control.
- Use `pyprojec.toml` in the project root for static settings that do not vary between environments (e.g. 
package settings)

## Deployment
- Use .dockerignore to keep deployment lean.

## Additional (Updated over time as the project grows)
- Take into account timezone-naive, aware implicit conversion between SQLite, schemas. 