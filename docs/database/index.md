# Database Commands 🗄️

If you already know how Alembic works and just need a quick reference for the commands you use every day, here they are! 🚀

---

## Common Commands 🛠️

| Command | What it does | Emoji |
| :--- | :--- | :---: |
| `alembic check` | Verify setup and detect unapplied changes | 🔍 |
| `alembic revision --autogenerate -m "..."` | Generate a new migration from model changes | ✨ |
| `alembic upgrade head` | Apply all pending migrations | ⬆️ |
| `alembic current` | Show which version the database is currently at | 📍 |
| `alembic history` | List all migrations in order | 📜 |
| `alembic downgrade -1` | Roll back the most recent migration | ⬇️ |

---

## When to use what? 🤔

*   **Just added a new column?** Run `check` first, then `revision --autogenerate`.
*   **Just pulled latest code from Git?** Run `upgrade head` to sync your local DB.
*   **Made a mistake in your last migration?** Run `downgrade -1`, fix your model, delete the bad migration file, and generate a new one.
