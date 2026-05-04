from typing import Annotated

from fastapi import Cookie, Depends, status
from fastapi import Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import (
    AlreadyAuthenticated,
    InvalidFormData,
    MalformedToken,
    UnauthenticatedUser,
    UsernameAlreadyExists,
    UserNotFound,
)
from src.auth.models import User
from src.auth.schemas import AuthCreate
from src.auth.service import (
    create_access_token,
    get_access_token_max_age_seconds,
    get_user_by,
    verify_token,
)
from src.database import get_db
from src.templates import Redirect


# =============== SSR REDIRECT HELPERS ===============
async def valid_cookie_token(
    db: Annotated[AsyncSession, Depends(get_db)],
    access_token: Annotated[str | None, Cookie()] = None,
) -> User | None:
    """
    Resolve the authenticated SSR user from a cookie.

    Returns None if the cookie is not valid.
    """
    try:
        return await verify_token(access_token, db)
    except (UnauthenticatedUser, MalformedToken, UserNotFound):
        return None


async def redirect_authenticated_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    access_token: Annotated[str | None, Cookie()] = None,
) -> None:
    """Redirect authenticated SSR users away from public auth pages.

    Raises:
        AlreadyAuthenticated: If the cookie resolves to a valid authenticated user.
    """
    if await valid_cookie_token(db, access_token):
        raise AlreadyAuthenticated


async def valid_registration_form(request: Request) -> AuthCreate:
    """Validate SSR registration form data and build an auth payload.

    Args:
        request: Incoming FastAPI request containing form data.

    Returns:
        AuthCreate: Validated registration payload.

    Raises:
        InvalidFormData: If the submitted form data cannot be validated.
    """
    form = await request.form()
    form_data = dict(form)
    try:
        return AuthCreate.model_validate(form_data)
    except ValidationError:
        raise InvalidFormData


async def no_duplicate_user_record(
    valid_form: Annotated[AuthCreate, Depends(valid_registration_form)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthCreate:
    """Ensure the validated registration username is unused.

    Args:
        valid_form: Validated registration form payload dependency.
        db: Async database session dependency.

    Returns:
        AuthCreate: Validated registration payload with an available username.

    Raises:
        UsernameAlreadyExists: If the submitted username is already taken.
    """
    if await get_user_by("username", valid_form.username, db):
        raise UsernameAlreadyExists

    return valid_form


def redirect_with_cookie(user: User, redirect_url: str = "/") -> RedirectResponse:
    """Create an auth cookie for the user and return a redirect response.

    Args:
        user: Authenticated user to encode into the access token.
        redirect_url: Target URL after the cookie is set.

    Returns:
        RedirectResponse: Redirect response with the auth cookie attached.
    """
    token = create_access_token(
        data={"sub": str(user.id), "role": str(user.role)},
    )

    response = RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,  # JS cannot access this
        secure=True,  # HTTPS only in production
        samesite="lax",  # CSRF protection
        max_age=get_access_token_max_age_seconds(),
    )
    return response


def redirect_remove_cookie() -> RedirectResponse:
    """Remove the auth cookie and redirect the user to home.

    Returns:
        RedirectResponse: Redirect response with the auth cookie removed.
    """
    response = Redirect.to_home()
    response.delete_cookie("access_token")

    return response
