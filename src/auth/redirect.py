from typing import Annotated

from fastapi import Cookie, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import (
    AlreadyAuthenticated,
    MalformedToken,
    UnauthenticatedUser,
    UserNotFound,
)
from src.auth.models import User
from src.auth.service import (
    create_access_token,
    get_access_token_max_age_seconds,
    verify_token,
)
from src.database import get_db
from src.templates import Redirect


# --------------- SSR REDIRECT HELPERS
async def redirect_authenticated_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    access_token: Annotated[str | None, Cookie()] = None,
) -> None:
    try:
        await verify_token(access_token, db)
    except (UnauthenticatedUser, MalformedToken, UserNotFound):
        return None

    raise AlreadyAuthenticated


def create_cookie(user: User, redirect_url: str = "/") -> RedirectResponse:
    """
    Create and store a JWT access token in an HTTP-only cookie AND redirect the user.
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


def logout() -> RedirectResponse:
    """
    Log out the user by removing the authentication cookie and redirecting to home.
    """
    response = Redirect.to_home()
    response.delete_cookie("access_token")
    return response
