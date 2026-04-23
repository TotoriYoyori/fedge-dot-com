# Containerization with Docker 🐳

FEDGE is containerized using a secure, optimized, and modern `Dockerfile` that leverages **UV** for dependency management.

---

## 1. Dockerfile Architecture 🏛️

Our Dockerfile is designed with three main goals: **Security**, **Speed**, and **Reproducibility**.

### Key Features:
- **UV Integration**: Uses the official UV binary for high-speed installs.
- **Layer Caching**: Dependencies are installed in a separate step from the source code to maximize cache hits.
- **Non-Root User**: The application runs as a `nonroot` user for enhanced security.
- **Bytecode Compilation**: Python files are pre-compiled during build to speed up container startup.

---

## 2. Secure Base Image 🛡️

We use `python:3.13-slim` as the base image. It provides a small footprint while including the necessary libraries for production. 

```dockerfile
FROM python:3.13-slim
```

---

## 3. The Build Process ⚙️

### Phase 1: Environment Setup
We copy the UV binary and set up environment variables for optimization.
```dockerfile
COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_DEV=1
```

### Phase 2: Dependency Sync
We sync dependencies before copying the rest of the code. This ensures that if you only change a line of Python code, Docker doesn't have to re-download all your packages.
```dockerfile
COPY uv.lock pyproject.toml ./
RUN uv sync --locked --no-install-project
```

### Phase 3: Security & Execution
We switch to a non-privileged user and set the final entrypoint.
```dockerfile
USER nonroot
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 4. Local Development with Docker 💻

To test the production container locally:

1. **Build the image**:
   ```bash
   docker build -t fedge-api .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8000:8000 --env-file .env fedge-api
   ```

3. **Verify**:
   Visit `http://localhost:8000/docs` to see the API documentation.

---

## 5. Production Considerations 🚀

- **Mounting Volumes**: Do not mount your local `.venv` into the container; the container builds its own environment.
- **Environment Variables**: Use a secret management system (like AWS Secrets Manager or HashiCorp Vault) to pass production `.env` variables into the container.
