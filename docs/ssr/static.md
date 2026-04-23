# Static Files 🖼️

Static files (CSS, JavaScript, Images) in FEDGE are organized to match our domain-driven architecture.

---

## 1. Organization 📂

- **Global Static**: Assets used across the entire application (e.g., brand logos, global reset CSS) live in `src/static/`.
- **Domain Static**: Assets specific to a module (e.g., `auth.css`, `home.js`) live in `src/<domain>/static/`.

---

## 2. Mounting Static Files 🛠️

FastAPI needs to be told where to find these files. This is handled in `src/main.py` using `app.mount`.

```python
# src/main.py
from fastapi.staticfiles import StaticFiles

# Mount domain-specific static folders
app.mount(
    "/static/auth", 
    StaticFiles(directory=BASE_DIR / "auth" / "static"), 
    name="auth-static"
)

# Mount the global static folder last
app.mount(
    "/static", 
    StaticFiles(directory=BASE_DIR / "static"), 
    name="static"
)
```

**Order Matters**: Always mount specific sub-paths (`/static/auth`) *before* the general path (`/static`) to avoid route shadowing.

---

## 3. Referencing Static Files in Templates 🔗

When linking to assets in your HTML templates, use the mounted path:

```html
<!-- Global CSS -->
<link rel="stylesheet" href="/static/css/global.css">

<!-- Domain CSS -->
<link rel="stylesheet" href="/static/auth/css/auth.css">

<!-- Images -->
<img src="/static/images/logo.png" alt="Fedge Logo">
```

---

## 4. Best Practices 💡

1.  **Unique Names**: Ensure your static sub-directories are named descriptively to avoid collision when mounting.
2.  **No url_for for Static**: While we use `url_for` for routes, standard paths (e.g., `/static/...`) are usually sufficient and more readable for static assets in this project.
3.  **Optimization**: Keep your static assets organized in sub-folders like `css/`, `js/`, and `images/` within each `static/` directory.
