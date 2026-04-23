# Package Management with UV 📦

FEDGE uses [UV](https://github.com/astral-sh/uv) as its primary package manager. UV replaces `pip`, `pip-tools`, `venv`, and `virtualenv` with a single, lightning-fast tool.

---

## 1. Setup 🛠️

If you don't have UV installed, follow the [official installation guide](https://github.com/astral-sh/uv#installation).

```bash
# Example for macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Example for Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## 2. Managing Dependencies ➕

UV manages dependencies in `pyproject.toml` and pins them in `uv.lock`.

### Adding a Package
To add a new production dependency (e.g., `httpx`):
```bash
uv add httpx
```

### Adding a Development Package
To add a package only for local development/testing (e.g., `pytest`):
```bash
uv add --dev pytest
```

### Removing a Package
```bash
uv remove <package_name>
```

---

## 3. The Lockfile (`uv.lock`) 🔒

The `uv.lock` file is automatically generated and updated. **Always commit this file to Git.** It ensures that every developer and the production server use the exact same version of every transitive dependency.

To update all packages to their latest compatible versions:
```bash
uv lock --upgrade
```

---

## 4. Virtual Environments 🌐

UV creates a `.venv` directory in the project root. You don't need to manually activate it if you use `uv run`.

- **To create/sync the environment**: `uv sync`
- **To run a command in the environment**: `uv run <command>` (e.g., `uv run python src/main.py`)
- **To manually activate** (standard way):
    - Windows: `.venv\Scripts\activate`
    - POSIX: `source .venv/bin/activate`

---

## 5. UV Optimization in CI/CD 🚀

In our Docker builds and CI pipelines, we use specialized UV flags:
- `--locked`: Fails if `uv.lock` is out of sync with `pyproject.toml`.
- `--no-install-project`: Installs dependencies without installing the actual project code (useful for layer caching).
- `UV_COMPILE_BYTECODE=1`: Compiles `.py` to `.pyc` during install for faster startup.
