# Redirects and Cookie Management 🧭

When building SSR applications, managing redirections and browser cookies is crucial for a smooth user experience. In FEDGE, we centralize this logic in `redirect.py`.

---

## 1. The `AuthRedirect` Class 🛡️

In the `auth` domain, `AuthRedirect` provides static methods to handle common redirection scenarios and cookie operations.

```python
from fastapi.responses import RedirectResponse
from src.auth.settings import auth_settings

class AuthRedirect:
    LOGIN_PAGE = "login.html"
    
    @staticmethod
    def to_home() -> RedirectResponse:
        """Standard 303 redirect to home page."""
        return RedirectResponse(url="/", status_code=303)

    @staticmethod
    def store_cookie(token: Token) -> RedirectResponse:
        """Sets the access_token cookie and redirects home."""
        response = AuthRedirect.to_home()
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        return response
```

---

## 2. Why Use a Redirect Helper? 🤔

1.  **Centralized URLs**: If the home page URL changes from `/` to `/home`, you only need to update it in one place.
2.  **Consistent Status Codes**: We prefer `303 See Other` for redirects after POST requests to prevent form re-submission issues.
3.  **Encapsulated Cookie Logic**: Cookie attributes (HttpOnly, Secure, SameSite) are managed centrally, ensuring security best practices are applied consistently.
4.  **Cleaner Controllers**: Your `pages.py` functions become more readable:
    ```python
    if not user:
        return AuthRedirect.to_home()
    ```

---

## 3. Cookie-Based Authentication 🍪

SSR routes use cookies instead of the `Authorization: Bearer` header used by APIs. 

- **Setting Cookies**: Done via `response.set_cookie()` during login or registration.
- **Reading Cookies**: Done via FastAPI's `Cookie()` dependency:
    ```python
    async def valid_cookie_token(access_token: Annotated[str | None, Cookie()] = None):
        ...
    ```
- **Clearing Cookies**: Done via `response.delete_cookie("access_token")` during logout.
