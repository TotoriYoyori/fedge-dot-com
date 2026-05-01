# Codebase audit: proposed tasks

This document proposes one actionable task in each requested category.

## 1) Typo fix task

**Task:** Fix duplicated wording in the login route description string.

- **Where:** `src/auth/router.py`
- **Issue:** The description says `"JWT access access_token"` (duplicated `access`).
- **Suggested change:** Update phrase to `"JWT access token"`.
- **Why it matters:** This appears in generated API docs and reduces perceived quality.

## 2) Bug fix task

**Task:** Prevent `require_role(..., use_cookie=True)` from crashing when cookie auth is missing/invalid.

- **Where:** `src/auth/dependencies.py`
- **Issue:** `valid_cookie_token()` explicitly returns `None` for invalid/missing tokens, but `require_role()` assumes `user` is always present and dereferences `user.role`.
- **Failure mode:** This can raise `AttributeError: 'NoneType' object has no attribute 'role'` and result in a 500 instead of a controlled auth response.
- **Suggested change:** In `checker()`, guard for `user is None` and raise `UnauthenticatedUser` (or a dedicated SSR auth exception) before role checking.
- **Why it matters:** Converts a server error into expected authentication behavior.

## 3) Code comment / documentation discrepancy task

**Task:** Align `AuthSecurity` class docstring method list with actual implementation names.

- **Where:** `src/auth/security.py`
- **Issue:** The class docstring lists `get_access_token_expires_at(...)`, but implemented method is `get_token_expiry_timestamp(...)`.
- **Suggested change:** Update the docstring method list to the real method name (or rename method if preferred and safe).
- **Why it matters:** Prevents confusion for contributors and docs readers.

## 4) Test improvement task

**Task:** Add regression tests for auth dependency edge cases and route docs text.

- **Where:** add new tests under a future `tests/` layout (e.g., `tests/auth/test_dependencies.py`, `tests/auth/test_openapi_docs.py`).
- **Suggested coverage:**
  1. `require_role(..., use_cookie=True)` with no cookie should produce an auth failure, not a 500.
  2. `require_role()` should reject users with disallowed roles.
  3. OpenAPI schema for `/api/v1/auth/login` should not contain duplicated phrase `"access access_token"` after typo fix.
- **Why it matters:** Locks in behavior and prevents regressions in auth control flow and public API docs.
