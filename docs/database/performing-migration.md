# Performing Migrations 🔄

Migrations are like **Save Points** in a video game. 🎮 They allow you to evolve your database schema (add tables, change columns) over time without losing your precious data.

---

## Prerequisites 📝

*   Alembic is set up (see [Alembic Setup](./alembic-setup.md)).
*   Your database is reachable.
*   All models are imported in `alembic/env.py`.

---

## 1. The Workflow 🏗️

Whenever you change your SQLAlchemy models, follow this 3-step dance:

### Step 1: Generate the script ✨
Ask Alembic to compare your models with the actual database:
```bash
alembic revision --autogenerate -m "add phone_number to users"
```
This creates a new "Migration Script" in `alembic/versions/`.

### Step 2: Review the script 🔍
**Never skip this!** While Alembic is smart, it's not perfect. Open the generated file and make sure the `upgrade()` and `downgrade()` functions do exactly what you expect.

### Step 3: Apply the changes ⬆️
Once you're happy, push the changes to the database:
```bash
alembic upgrade head
```

---

## 2. Handling New Models 🤱

When adding a brand new model file (e.g., `src/products/models.py`):

1.  **Inherit**: Ensure your model inherits from `src.database.Base`.
2.  **Import**: Open `alembic/env.py` and import your new model. If you forget this, Alembic will be "blind" to your new table! 🙈
3.  **Generate & Apply**: Follow the workflow above.

---

## ⚠️ The Golden Rule

**Always perform your migration BEFORE starting your FastAPI service.** 

If you start the app first, SQLAlchemy might create the tables automatically (depending on your setup), and Alembic won't be able to track that change properly. Always let Alembic lead the way! 🧭
