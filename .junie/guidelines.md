# FastAPI Guidelines

You are an expert in Python, FastAPI, and scalable async web application development. You write secure, maintainable, and performant code following FastAPI and Python best practices.

## General
- Do not commit to Git without consent from me.
- Do not perform more tasks than is outlined the prompt.
- Ask clarifying questions if you need more context. Do not assume you know 
better than me.
- All changes must be roll-backable (do not introduce irrevertible changes).
- Ignore `src/dummies` folder for tasks, unless specifically assigned by me. This folder 
is meant to be my own sandbox.

## Python Best Practices
- Follow PEP 8 with a 120 character line limit
- Use double quotes for Python strings
- Sort imports with `isort`, code formatting with `black`.
- Use f-strings for string formatting
- Use type hints everywhere — parameters, return types, and class attributes

## Async First Approach
- Use async-first design — prefer `async def` routes for all I/O-bound operations. 
- Never call blocking operations (e.g. `time.sleep`, sync DB calls) inside `async` routes; use `await` equivalents 
or offload to a threadpool. 
- Use `asyncer` library to smoothly call sync code as async (`asyncer.asyncify`), or async as sync (`asyncer.syncify`)


## FastAPI Best Practices
- Use Pydantic extensively for input validation, output serialization, and settings management
- Use dependency injection via `Depends()` for shared logic — do not repeat auth, DB session, or permission checks inline in routes
- Prefer FastAPI's built-in features (dependencies, response models, status codes) before reaching for third-party packages

## Project Structure
- Follow a domain-driven layout, grouping files by feature module rather than file type
- Each module lives in its own directory under `src/` and contains: `router.py`, `schemas.py`, `models.py`, `service.py`, `dependencies.py`, `constants.py`, `exceptions.py`, `utils.py` — include only what the module needs
- `src/main.py` is the app entry point; keep it thin — only app initialization and router registration
- Global shared concerns (database session, pagination, base exceptions, global config) live directly in `src/`
- When importing across modules, use explicit module-level imports to avoid circular dependencies:
```python
from src.auth import constants as auth_constants
from src.notifications import service as notification_service
```


## Schemas (Pydantic)
- Define separate schemas for request input, response output, and DB representation — never reuse the same schema for all three
- Use a shared `CustomBaseModel` to enforce project-wide conventions (e.g. `alias_generator`, `populate_by_name`)
- Use `model_validator` and `field_validator` for cross-field validation logic instead of putting it in routes or services.
Only add this if dealing with more complex validations that Pydantic doesn't already handle with type hints and Field.
- Never return raw ORM objects from routes — always serialize through a response schema with `response_model`

## Routes
- Keep route functions thin — delegate all business logic to `service.py`
- Always set explicit `response_model`, `status_code`, and `summary` on route decorators
- Validate and document all possible response codes using the `responses` parameter for OpenAPI accuracy
- Use `HTTPException` with explicit status codes; never let unhandled exceptions surface to the client
- Always validate and sanitize user input through Pydantic schemas — never trust raw request data

## Dependencies
- Place all reusable route dependencies in the module's `dependencies.py`, not in `service.py`
- Use dependency chaining to build layered authorization or context (e.g. `get_current_user` → `require_role("admin")`)
- Prefer `async` dependencies for anything that touches the database or external services
- Use `Depends()` at the router level for dependencies shared across all routes in a module

## Services
- `service.py` contains only business logic — no FastAPI imports, no `Request`, no `Depends`
- Services are plain async functions that accept typed arguments and return typed results
- Keep services independently testable without needing to spin up the full app

## Exceptions
- Define module-specific exceptions in `exceptions.py` (e.g. `PostNotFound`, `InvalidCredentials`)
- Register global exception handlers in `main.py` to convert domain exceptions to `HTTPException` responses
- Never raise `HTTPException` from inside `service.py` — services should raise domain exceptions only

## Models (SQLAlchemy)
- Define all SQLAlchemy models in the module's `models.py` with explicit column types and constraints
- Column naming should be snake_case singular form(e.g. `name`, `email`, `like_post_id`, etc.)
- Use `__tablename__` in snake_case plural form (e.g. `posts`, `user_profiles`)
- Use `_time` suffix for datetime columns and `_date` suffix for date columns
- Always define indexes explicitly and follow a consistent naming convention via SQLAlchemy `MetaData`

## Database
- Use Alembic for all schema migrations — never mutate the DB schema manually
- Write migrations that are static and reversible; use the `date_slug` file template (e.g. `2024-08-24_add_post_index.py`)
- Use `select_related` patterns (SQLAlchemy `joinedload` / explicit joins) to avoid N+1 query problems
- Prefer doing complex joins and aggregations in SQL rather than in Python
- Never use raw SQL strings unless absolutely necessary, and always parameterize inputs if you do

## Settings & Configuration
- Manage all configuration through a Pydantic `BaseSettings` class in `src/config.py`
- Load values from environment variables; never hardcode secrets or environment-specific values
- Never commit `.env` files or secrets to version control.
- Use module-level `config.py` for domain-specific settings that don't belong globally
- Use `pyprojec.toml` in the project root for static settings that do not vary between environments (e.g. 
package settings)
