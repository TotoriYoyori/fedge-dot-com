# Deployment & Environment Overview 🚀

This section covers how FEDGE is packaged, managed, and deployed. We have recently transitioned to **UV** for extremely fast package management and updated our **Dockerfile** to follow modern production best practices.

---

## Quick Cheatsheet ⚡

### Working with UV
| Task | Command |
| :--- | :--- |
| **Sync Environment** | `uv sync` |
| **Add Dependency** | `uv add <package>` |
| **Add Dev Dependency** | `uv add --dev <package>` |
| **Run App Locally** | `uv run uvicorn src.main:app --reload` |
| **Lock dependencies** | `uv lock` |

### Working with Docker
| Task | Command |
| :--- | :--- |
| **Build Image** | `docker build -t fedge-api .` |
| **Run Container** | `docker run -p 8000:8000 --env-file .env fedge-api` |
| **Check Logs** | `docker logs <container_id>` |

---

## Why UV + Docker? 🛠️

- **Speed**: UV is written in Rust and is significantly faster than pip/pip-tools.
- **Reproducibility**: `uv.lock` ensures every environment (Dev, CI, Prod) uses the exact same versions.
- **Security**: Our Dockerfile uses a non-root user and minimal base images (`python-slim`).
- **Efficiency**: UV's caching mechanism and layer optimization keep Docker builds fast.

---

## Navigation 🗺️

- **[Package Management with UV](uv.md)**: How to manage dependencies, venvs, and locks.
- **[Containerization with Docker](docker.md)**: Deep dive into our multi-stage, secure Dockerfile.
