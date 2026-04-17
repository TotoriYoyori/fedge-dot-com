# Alembic Setup 🛰️

Alembic is the **Time Machine** for your database. 🕰️ It allows you to "save" the state of your database schema and "travel" between different versions as your project evolves.

---

## Prerequisites 📝

*   A Python virtual environment is **active**. 🐍
*   SQLAlchemy and your database driver are installed.
*   `src/database.py` exists and exposes a `Base`.
*   `src/config.py` exists and exposes `settings.DATABASE_URL`.

---

## 1. Install Alembic 📦

```bash
pip install alembic
```

---

## 2. Initialise the environment 🏗️

Run this from your project root:

```bash
alembic init alembic
```

This creates the `alembic/` folder and `alembic.ini`. Think of `alembic/` as the **logbook** of your database's history. 📜

---

## 3. Configure `alembic.ini` ⚙️

We need to tell Alembic how to behave. Update your `alembic.ini` (specifically the `[alembic]` section) to match this. This ensures your migration files are named with dates, making them easy to sort! 📅

```ini
[alembic]
script_location = alembic
file_template = %%(year)d-%%(month).2d-%%(day).2d_%%(slug)s
prepend_sys_path = .
```

---

## 4. Configure `alembic/env.py` 🧬

This file is the **brain** of Alembic. It connects your SQLAlchemy models to the migration tool. Replace the generated `env.py` with the code below.

**Important**: You must import all your models here so Alembic can "see" them!

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from src.config import settings
from src.database import Base

# ----- Import all your SQLAlchemy models here -----
# Example: from src.users.models import User
# --------------------------------------------------

config = context.config
target_metadata = Base.metadata

# Convert async URL to sync for Alembic
sync_url = settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")
config.set_main_option("sqlalchemy.url", sync_url)

def run_migrations_offline() -> None:
    """Run in 'offline' mode (useful for generating SQL scripts)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run in 'online' mode (against a real database)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## 5. Verify and Generate 🚀

### Step A: The "Check-up" 🔍
Verify that Alembic can reach your database and see your models:
```bash
alembic check
```

### Step B: The First Migration ✨
Create your initial "Save Point":
```bash
alembic revision --autogenerate -m "initial schema"
```

### Step C: Apply ⬆️
Make it real in the database:
```bash
alembic upgrade head
```

---

## Pro-Tip: Adding New Models 💡

Whenever you add a new model:

1.  **Import** it in `alembic/env.py`.

2.  **Generate** a new revision: `alembic revision --autogenerate -m "..."`.
 
3.  **Upgrade**: `alembic upgrade head`.
