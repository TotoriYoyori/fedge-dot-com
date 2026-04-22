from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.auth.redirect import AuthRedirect
from src.templates import templates


class UsernameAlreadyExists(Exception):
    pass


class InvalidFormData(Exception):
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


def _is_browser_request(request: Request) -> bool:
    return "text/html" in request.headers.get("accept", "")


def _render_error(request: Request, page: str, error: str, status_code: int):
    return templates.TemplateResponse(
        request=request,
        name=page,
        context={"error": error},
        status_code=status_code,
    )


def register_exception_handlers(app) -> None:
    @app.exception_handler(InvalidFormData)
    async def invalid_form_data_handler(request: Request, exc: InvalidFormData):
        if _is_browser_request(request):
            return _render_error(
                request,
                AuthRedirect.REGISTER_PAGE,
                "Please provide a valid username, email, and password.",
                status.HTTP_400_BAD_REQUEST,
            )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid form data."},
        )

    @app.exception_handler(UsernameAlreadyExists)
    async def username_already_exists_handler(
        request: Request, exc: UsernameAlreadyExists
    ):
        if _is_browser_request(request):
            return _render_error(
                request,
                AuthRedirect.REGISTER_PAGE,
                "Username already taken, please choose another one.",
                status.HTTP_409_CONFLICT,
            )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Username already exists."},
        )

    @app.exception_handler(UnauthenticatedUser)
    async def unauthenticated_user_handler(
        request: Request, exc: UnauthenticatedUser
    ):
        if _is_browser_request(request):
            return _render_error(
                request,
                AuthRedirect.LOGIN_PAGE,
                "Invalid username or password.",
                status.HTTP_401_UNAUTHORIZED,
            )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Unauthenticated. Incorrect username or password."},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(MalformedToken)
    async def malformed_token_handler(request: Request, exc: MalformedToken):
        if _is_browser_request(request):
            return AuthRedirect.to_home()
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Malformed access_token. Please log in and try again."},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(UserNotFound)
    async def user_not_found_handler(request: Request, exc: UserNotFound):
        if _is_browser_request(request):
            return AuthRedirect.to_home()
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "User not found."},
        )

    @app.exception_handler(AlreadyAuthenticated)
    async def already_authenticated_handler(
        request: Request, exc: AlreadyAuthenticated
    ):
        if _is_browser_request(request):
            return AuthRedirect.to_home()
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Already authenticated."},
        )

    @app.exception_handler(InsufficientPermission)
    async def insufficient_permission_handler(
        request: Request, exc: InsufficientPermission
    ):
        if _is_browser_request(request):
            return AuthRedirect.to_home()
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Insufficient permissions"},
        )
