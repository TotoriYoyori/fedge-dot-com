# Server-Side Rendering (SSR) Support 🖥️

FEDGE supports full Server-Side Rendering using **Jinja2** templates. This allows us to build fast, SEO-friendly, and interactive web interfaces within the same FastAPI codebase.

---

## 1. Template Discovery System 🔍

We use a dynamic template discovery mechanism in `src/templates.py`. Instead of a single monolithic templates folder, the engine automatically searches for `templates/` directories in:

1. `src/templates/` (Global base templates)
2. `src/<domain>/templates/` (Domain-specific templates)

This keeps our frontend code grouped with its relevant business logic.

### How it works
The discovery logic uses `pathlib` to scan the `src/` directory for any folder named `templates/`.

```python
# src/templates.py

def _discover_dirs(folder_name: str) -> list[str]:
    dirs: list[str] = []

    # ----- Search Base and Domains
    shared_dir = SRC_DIR / folder_name
    if shared_dir.exists():
        dirs.append(str(shared_dir))

    for path in sorted(SRC_DIR.iterdir()):
        candidate = path / folder_name
        if path.is_dir() and candidate.exists():
            dirs.append(str(candidate))

    return dirs

# Initialize Jinja2 with all discovered paths
page_loader = FileSystemLoader(_discover_dirs("templates"))
page_env = Environment(loader=page_loader)
templates = Jinja2Templates(env=page_env)
```

---

## 2. Static Assets 🎨

Static files (CSS, JS, Images) are organized similarly:

- **Global Assets**: Located in `src/static/`, mounted at `/static`.
- **Domain Assets**: Located in `src/<domain>/static/`, mounted individually in `src/main.py`.

### Mounting in `main.py`
Each domain that requires its own static assets must have its directory mounted:

```python
# src/main.py

app.mount(
    "/static/auth",
    StaticFiles(directory=BASE_DIR / "auth" / "static"),
    name="auth-static",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
```

---

## 3. SSR Best Practices 🛠️

When developing SSR features, follow these patterns to ensure consistency and maintainability.

### A. Use `pages.py` for Routes
Keep HTML-returning routes separate from JSON-returning API routes (`router.py`).

```python
# src/auth/pages.py

@page.get("/login", **RouteDecoratorPreset.html_get())
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={},
    )
```

### B. Use `RouteDecoratorPreset`
Use `**RouteDecoratorPreset.html_get()` or `html_post()` in your decorators to ensure consistent response classes and status codes.

```python
# src/schemas.py

class RouteDecoratorPreset:
    @staticmethod
    def html_get() -> dict:
        return {
            "response_model": None,
            "response_class": HTMLResponse,
            "status_code": status.HTTP_200_OK,
        }
```

### C. Dynamic URLs in Templates
Always use `{{ request.url_for('name') }}` in Jinja2 templates instead of hardcoding paths. This ensures links don't break if the routing structure changes.

```html
<!-- src/auth/templates/login.html -->
<form action="{{ request.url_for('login_submit') }}" method="post">
    <!-- ... -->
</form>
```

### D. Redirect Helpers
Centralize complex redirect logic and cookie management (like JWT storage) in `redirect.py`.

```python
# src/auth/redirect.py

class AuthRedirect:
    @staticmethod
    def store_cookie(token: Token) -> RedirectResponse:
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,
            samesite="lax",
        )
        return response
```
