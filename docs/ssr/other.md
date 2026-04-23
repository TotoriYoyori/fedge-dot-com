# Other SSR Considerations 🛠️

Building a robust SSR application involves more than just routes and templates. Here are some other important patterns we use in FEDGE.

---

## 1. Domain Error Handlers 🚨

Handling exceptions in SSR is different from APIs. Instead of returning a JSON error, we want to show a friendly error page or redirect the user.

We use `register_exception_handlers(app)` in `main.py` to catch domain-specific exceptions and render appropriate HTML responses.

### Example Handler
```python
# src/auth/exceptions.py
def register_exception_handlers(app):
    @app.exception_handler(UnauthenticatedUser)
    async def unauthenticated_user_handler(request: Request, _exc):
        if "text/html" in request.headers.get("accept", ""):
            return templates.TemplateResponse(
                request=request,
                name="login.html",
                context={"error": "Invalid username or password."},
                status_code=401
            )
        return JSONResponse(status_code=401, content={"detail": "..."})
```

---

## 2. Form Validation (Pydantic) 📝

Even though SSR uses HTML forms (form-data), we still use Pydantic for validation.

```python
@page.post("/register")
async def register_submit(request: Request):
    form = await request.form()
    try:
        # Validate form-data using the same schema as the API
        auth_create = AuthCreate.model_validate(dict(form))
    except ValidationError:
        raise InvalidFormData
    ...
```

---

## 3. SSR-Specific Dependencies 💉

Some dependencies are tailored specifically for SSR, such as `valid_cookie_token`. Unlike API dependencies, these often return `None` or redirect instead of raising `401 Unauthorized`, allowing the page to render in a "logged-out" state.

---

## 4. Mixing SSR and API 🤝

In a modern application, you might have an SSR page that uses JavaScript to call an API. 
- The page is served by `pages.py`.
- The JavaScript in that page calls endpoints in `router.py`.

FEDGE supports this hybrid approach by mounting both routers and allowing cross-module imports.
