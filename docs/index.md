# FEDGE { #fedge }

<style>
.md-content .md-typeset h1 { display: none; }
</style>

<p align="center">
  <img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" alt="FEDGE" width="200">
</p>

<p align="center">
    <em><b>F</b>ast <b>E</b>mail & <b>D</b>ata <b>G</b>ateway <b>E</b>ngine</em>
</p>

<p align="center">
    <em>A high-performance, async-first API for managing emails, notifications, and user authentication.</em>
</p>

---

Welcome to **FEDGE**! 🚀 This service is designed to be the backbone of your email and notification workflows, built with the speed and elegance of **FastAPI** and the robustness of **SQLAlchemy**.

Whether you are here to integrate Google OAuth, send beautifully designed notification emails, or manage users, you're in the right place.

---

## Core Pillars 🏛️

FEDGE is built on four main modules, each handling a specific part of your application's lifecycle:

*   **🔐 Auth**: Secure registration and login using JWT tokens. It handles roles (Admin, Merchant, User) so you can control who does what.
*   **📧 Google Integration**: Seamlessly connect Gmail accounts via OAuth2 to read inboxes and manage credentials.
*   **🔔 Notifications**: A powerful engine to send formatted emails. It even includes a designer to preview your templates! 🎨
*   **👥 User Management**: Administrative tools to keep your user base organized.

---

## Why FEDGE? 🤔

We believe complex systems should feel simple. Here’s how we turn "hard" things into "easy" ones:

### ⚡ Async Everywhere
Think of **Async** like a smart waiter in a restaurant. 🍽️ Instead of standing still waiting for the chef to finish your steak, they go and serve other tables. FEDGE uses `async` for all database and network operations, meaning we don't waste time waiting; we keep serving.

### 💉 Dependency Injection
This sounds intimidating, but it's just "asking for what you need." 📥 When a route needs a database connection, it just asks for `db: AsyncSession = Depends(get_db)`. FEDGE handles the magic of creating, giving, and safely closing that connection for you.

### ⏳ Database Migrations (Alembic)
Your database schema is like a living organism. 🧬 As your app grows, the database needs to change too. We use **Alembic** to track these changes like "Save Points" in a video game. If something goes wrong, you can always roll back to a previous version.

---

## Tech Stack 🛠️

FEDGE stands on the shoulders of modern Python giants:

*   **[FastAPI](https://fastapi.tiangolo.com/)**: The high-performance web framework.
*   **[SQLAlchemy 2.0](https://www.sqlalchemy.org/)**: The industry-standard ORM (Object-Relational Mapper) for interacting with databases.
*   **[Pydantic](https://docs.pydantic.dev/)**: For lightning-fast data validation and settings management.
*   **[Alembic](https://alembic.sqlalchemy.org/)**: For version-controlling your database schema.

---

## Getting Started 🏁

Ready to dive in? Here is how to navigate our documentation:

1.  **[Virtual Environments](./learn/venv-setup.md)**: Get your local environment ready. 🐍
2.  **[Database Setup](./learn/learn/database/database-setup.md)**: Wire up your database and engine. 🗄️
3.  **[Alembic Setup](./learn/learn/database/alembic-setup.md)**: Prepare for your first migration. 🛰️
4.  **[Performing Migrations](./learn/learn/database/performing-migration.md)**: Learn the "Generate -> Review -> Apply" workflow. 🔄

---

## Final Note 📝

This project follows a **domain-driven design**. Each feature lives in its own "home" inside `src/`, keeping the code clean, testable, and easy to find.

Now, go forth and build something awesome! **Nier Automata.** 🤖✨