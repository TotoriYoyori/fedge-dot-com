from fastapi import Request, status
from fastapi.responses import JSONResponse, RedirectResponse

class UsernameAlreadyExists(Exception):
    pass


class UnauthenticatedUser(Exception):
    pass


class MalformedToken(Exception):
    pass


class UserNotFound(Exception):
    pass


class AlreadyAuthenticated(Exception):
    pass


class InsufficientPermission(Exception):
    pass


# ----- APP HANDLERS
def register_exception_handlers(app) -> None:

    @app.exception_handler(UsernameAlreadyExists)
    async def username_already_exists_handler(request: Request, exc: UsernameAlreadyExists):
        """Raised when a username is already taken during registration."""
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Username already exists. Please register with a different username."},
        )

    @app.exception_handler(UnauthenticatedUser)
    async def unauthenticated_user_handler(request: Request, exc: UnauthenticatedUser):
        """Raised when incorrect username or password."""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Unauthenticated. Incorrect username or password."},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(MalformedToken)
    async def malformed_token_handler(request: Request, exc: MalformedToken):
        """Raised when a JWT access_token is malformed or invalid."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Malformed access_token. Please log in and try again."},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(UserNotFound)
    async def user_not_found_handler(request: Request, exc: UserNotFound):
        """Raised when a user is not found in the database."""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "User not found."},
        )

    @app.exception_handler(AlreadyAuthenticated)
    async def already_authenticated_handler(request: Request, exc: AlreadyAuthenticated):
        """Raised when an authenticated user tries to access a guest-only resource."""
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Already authenticated. Logout to access this resource."},
        )

    @app.exception_handler(InsufficientPermission)
    async def insufficient_permission_handler(request: Request, exc: InsufficientPermission):
        """Raised when an authenticated user has insufficient permissions for a resource."""
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Insufficient permissions"},
        )

    # FIXME: Refactor to have a separate handler for SSR flow.
    # ----- SSR handlers — redirect instead of JSON
    @app.exception_handler(UnauthenticatedUser)
    async def unauthenticated_handler(request: Request, exc: UnauthenticatedUser):
        if "text/html" in request.headers.get("accept", ""):
            return RedirectResponse(url="/login", status_code=303)

        return await unauthenticated_user_handler(request, exc)