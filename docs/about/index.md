# Project Architecture 🏗️

Welcome to the **Project Architecture** guide! This document serves as a quickstart for developers to understand the structural DNA of FEDGE. 

We follow a **Domain-Driven Design (DDD)**, meaning we group our code by "what it does for the user" (Features) rather than "what it is for the computer" (Types).

---

## 1. Project Structure Overview 🗺️

FEDGE is organized to be scalable, maintainable, and easy to navigate. Here is the high-level layout of the entire project:

```text
.
├── alembic/            # Database migration scripts and versioning
├── docs/               # Project documentation (MkDocs)
├── requirements/       # Environment-specific dependency lists
│   ├── base.txt        # Core dependencies (FastAPI, SQLAlchemy, Pydantic)
│   ├── dev.txt         # Development tools (pytest, black, isort)
│   └── prod.txt        # Production-only requirements
├── src/                # The Heart: Main source code
│   ├── auth/           # Domain: Authentication & Authorization
│   ├── google/         # Domain: Google OAuth & Gmail integration
│   ├── landing/        # Domain: Landing pages and SSR content
│   ├── notification/   # Domain: Email engine & Template designer
│   ├── orders/         # Domain: Order processing logic
│   ├── static/         # Global static assets
│   ├── templates/      # Global templates (base layouts, shared partials)
│   ├── users/          # Domain: User management
│   ├── config.py       # Global configuration management
│   ├── database.py     # Database engine and session setup
│   ├── main.py         # App entry point and router registration
│   ├── schemas.py      # Global base schemas and settings classes
│   └── templates.py    # Jinja2 template engine & discovery logic
├── tests/              # Automated test suites mirroring src/
├── alembic.ini         # Alembic configuration
├── docker-compose.yml  # Docker orchestration (if applicable)
├── Dockerfile          # Container definition (UV-optimized)
├── mkdocs.yml          # Documentation configuration
├── pyproject.toml      # Build system and tool configuration (UV)
└── uv.lock             # Deterministic dependency lockfile (UV)
```

---

## 2. Domain Structure 🚀

Each folder within `src/` represents a self-contained **Domain Module**. This modular approach ensures that features are decoupled and can be maintained independently.

### Comprehensive Module Anatomy

A typical domain module (e.g., `src/auth/`) is composed of the following components:

| File | Role | Description |
| :--- | :--- | :--- |
| `router.py` | **The Face** | Defines API endpoints using `APIRouter`. Maps HTTP requests to service functions. |
| `pages.py` | **The View** | Contains routes for Server-Side Rendering (SSR) that return `HTMLResponse`. |
| `redirect.py` | **The Guide** | (Optional) Domain-specific redirect helpers (e.g., `AuthRedirect`) for SSR flows. |
| `service.py` | **The Brain** | Houses business logic. It remains independent of FastAPI dependencies and focuses on data processing. |
| `models.py` | **The Skeleton** | SQLAlchemy ORM models defining the database schema for this domain. |
| `schemas.py` | **The Filter** | Pydantic models for request validation (Input) and response serialization (Output). |
| `dependencies.py`| **The Guard** | Reusable logic for route protection (e.g., `get_current_user`, permission checks). |
| `settings.py` | **The Heart** | Domain-specific configuration (e.g., SMTP settings for notifications). Often inherits from `DomainSettings`. |
| `exceptions.py` | **The Voice** | Custom domain exceptions that provide clear error signaling. |
| `constants.py` | **The Law** | (Optional) Domain-specific constants, enums, or fixed values. |
| `utils.py` | **The Hand** | (Optional) Helper functions specific to the domain's internal logic. |
| `templates/` | **The Canvas** | (Optional) Jinja2 HTML templates for SSR or email generation. |
| `static/` | **The Style** | (Optional) Static assets (CSS, JS, Images) served by the module. |

### Module Communication
When importing across modules, we use **explicit module-level imports** to avoid circular dependencies and maintain clarity:
```python
from src.auth import service as auth_service
from src.notification import schemas as notification_schemas
```

---

## 3. Server-Side Rendering (SSR) Support 🖥️

FEDGE supports full Server-Side Rendering (SSR) using Jinja2 templates. To keep this guide focused on general 
architecture, we have dedicated a separate section for SSR implementation details.

👉 **[Read the SSR Support Guide](../ssr/index.md)**

---

## 4. Environment Configuration 🔐

### `.env`
We use `.env` files to manage secrets and environment-specific settings. 

**CRITICAL: NEVER COMMIT YOUR `.env` FILE TO THE CODEBASE.**

| Type of `.env` | Purpose | Example |
| :--- | :--- | :--- |
| **Local** | Your personal dev settings; never shared. | `DATABASE_URL=sqlite:///db.sqlite3` |
| **Deployment** | Settings for the cloud/production server. | `DATABASE_URL=postgres://user:pass@db:5432/prod` |

---

## Database Evolution 🧬

We use **Alembic** to track changes to our database. Think of it as "Git for your data structure." 

1. **Models** change in `models.py`.
2. **Migrations** are generated in `alembic/versions/`.
3. **Schema** is updated by running the migration.

---

## Testing Strategy 🧪

### `/tests`
Quality is not an accident. We organize tests to mirror our source structure:

* **Unit Tests**: Testing individual functions in `service.py`.
* **Integration Tests**: Testing full API flows via `router.py`.

Always use **Dependency Injection** (like `get_db`) to make your code "testable." This allows us to swap a real database for a fast, in-memory one during tests.

---

## Summary 📝

By following this structure, we ensure that:
1. **New developers** can find code easily.
2. **The app** remains fast and async-first.
3. **Deployment** is predictable and secure using **UV** and **Docker**.

Now that you know the architecture, you're ready to start building! 🛠️✨
