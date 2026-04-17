# Database Setup 🗄️

FastAPI is an **async-first** framework. ⚡ Think of it like a smart receptionist who can handle multiple calls at once instead of making everyone wait. To keep up with this speed, we use **SQLAlchemy 2.0** as our async bridge to the database.

---

## Prerequisites 📝

*   A Python virtual environment is **active**. 🐍
*   `sqlalchemy` and a database driver (like `aiosqlite`) are installed.
*   Your `src/config.py` has a `DATABASE_URL`.

---

## 1. Naming Convention 🏷️

Ever try to rename a person who doesn't have a name? It's hard!
Databases need names for "Constraints" (like Unique keys or Indexes). If we don't name them consistently, **Alembic** (our migration tool) might get confused between different computers.

```python
NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
```

---

## 2. Declarative Base 🏗️

The `Base` class is the **parent** of all your models. 🤱 When you create a `User` model that inherits from `Base`, it automatically signs up for "Schema Monitoring," allowing Alembic to track every change you make.

```python
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
```

---

## 3. Engine and Session Factory 🏭

*   **The Engine**: The physical pipe connecting your app to the database. 🚰
*   **The Session Factory**: A machine that creates "Sessions" (brief conversations with the DB) whenever a request comes in.

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.config import settings

# The pipe
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# The conversation maker
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
```

---

## 4. Database Dependency 💉

In FastAPI, we "inject" what we need. When a route needs to talk to the database, it just asks for a session. We use an **Async Generator** to ensure the session is always closed safely, even if things go wrong. 🛡️

```python
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

---

## Complete `src/database.py` 📜

Copy and paste this into your project for a perfect setup:

```python
from typing import AsyncGenerator
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from src.config import settings

NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```
