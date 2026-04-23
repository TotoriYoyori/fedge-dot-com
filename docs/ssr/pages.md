# Pages and SSR Routes 📄

In FEDGE, we separate API routes from SSR (Server-Side Rendering) routes to keep our controllers clean and focused. While `router.py` handles JSON data for APIs, `pages.py` handles HTML rendering for browsers.

---

## 1. The `pages.py` Pattern 🏗️

Each domain module that provides a web interface includes a `pages.py` file. This file uses FastAPI's `APIRouter` but specifically returns `HTMLResponse`.

### Typical `pages.py` Structure

```python
from typing import Annotated
from fastapi import APIRouter, Depends, Request
from src.templates import templates
from src.schemas import RouteDecoratorPreset
from src.auth.dependencies import valid_cookie_token

page = APIRouter(tags=["ssr"])

@page.get(
    "/dashboard",
    name="dashboard_page",
    **RouteDecoratorPreset.html_get(),
)
async def dashboard(
    request: Request,
    current_user: Annotated[User | None, Depends(valid_cookie_token)],
):
    if not current_user:
        return AuthRedirect.to_home()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"user": current_user},
    )
```

---

## 2. Route Decorator Presets 🎨

To ensure consistency across SSR routes, we use `RouteDecoratorPreset` from `src/schemas.py`. This centralizes common parameters like `response_class=HTMLResponse` and standard OpenAPI response codes.

- **`html_get()`**: Sets up a standard 200 OK HTML response.
- **`html_post()`**: Sets up a standard HTML response for form submissions.

---

## 3. Best Practices 💡

1.  **Named Routes**: Always provide a `name` to your routes (e.g., `name="login_page"`). This allows you to use `request.url_for('login_page')` in your Jinja2 templates, making your code resilient to URL changes.
2.  **Request Object**: Always include `request: Request` in your route parameters, as it is required by Jinja2 to render templates.
3.  **Dependency Injection**: Use dependencies like `valid_cookie_token` to handle authentication via cookies seamlessly.
4.  **Lean Controllers**: Keep logic in `pages.py` minimal. Delegate complex data fetching to `service.py` and redirection logic to `redirect.py`.
