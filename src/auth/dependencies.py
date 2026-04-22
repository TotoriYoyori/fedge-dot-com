from typing import Annotated, Callable

from fastapi import Cookie, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import (
    AlreadyAuthenticated,
    InsufficientPermission,
    MalformedToken,
    UnauthenticatedUser,
    UsernameAlreadyExists,
    UserNotFound,
)
from src.auth.models import User
from src.auth.schemas import AuthCreate
from src.auth.security import AuthSecurity, oauth2_scheme
from src.auth.service import AuthService
from src.database import get_db


# --------------- PRIVATE
async def _verify_token(access_token: str, db: AsyncSession) -> User:
    """
    Shared core logic for access_token verification and user retrieval.
    Used by both Bearer (API) and cookie (SSR) auth flows.
    """
    if not access_token:
        raise UnauthenticatedUser

    payload = AuthSecurity.verify_access_token(access_token)
    if not payload:
        raise MalformedToken

    user_id = payload.get("sub")
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise MalformedToken

    user = await AuthService.get_one_by("id", user_id_int, db)
    if not user:
        raise UserNotFound

    return user


# --------------- ORM-RETURNING VALIDATION (valid_*, required_role)
async def valid_login_credentials(
    login_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Verifies user identity during the login process to ensure only users with valid
    credentials can obtain an authentication access_token.

    :param login_form: The submitted username and password from the login request.
    :param db: The database session for user lookup.
    :return: The authenticated User object if credentials are valid.
    """
    user = await AuthService.get_one_by("username", login_form.username, db)
    if not user or not AuthSecurity.verify_password(
        login_form.password, user.password_hash
    ):
        raise UnauthenticatedUser

    return user


async def valid_access_token(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Protects sensitive routes by validating the Bearer access_token and retrieving the
    associated user to establish an authenticated context. For API clients.

    :param token: The JWT access access_token provided in the Authorization header.
    :param db: The database session for user retrieval.
    :return: The authenticated User object associated with the access_token.
    """
    return await _verify_token(token, db)


async def valid_cookie_token(
    db: Annotated[AsyncSession, Depends(get_db)],
    access_token: Annotated[str | None, Cookie()] = None,
) -> User | None:
    """Returns User if logged in, None if not. Never raises."""
    try:
        return await _verify_token(access_token, db)
    except (UnauthenticatedUser, MalformedToken, UserNotFound):
        return None


def require_role(*roles: str, use_cookie: bool = False) -> Callable:
    """
    Enforces specific authorization levels across different routes to restrict 
    access based on user permissions. Use cookies for SSR-flows and no cookies for API route.

    :param roles: One or more role names permitted to access the resource.
    :param use_cookie: Whether to use cookie or not.
    :return: A dependency function that validates the user's role. Will return the current user
    at the end of the flow in addition to roles.
    """
    check_cookie_or_token = valid_cookie_token if use_cookie else valid_access_token

    async def checker(user: Annotated[User, Depends(check_cookie_or_token)]) -> User:
        if user.role not in roles:
            raise InsufficientPermission
        return user

    return checker


# --------------- EXISTENCE BOOL CHECKER (*_exists)
async def authenticated_exists(
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> bool | None:
    """
    Prevents already logged-in users from accessing authentication pages like login 
    or register to maintain clean navigation flow.

    :param token: The access access_token from the request, if any.
    :return: True if the user is not authenticated, allowing them to proceed.
    """
    if token and AuthSecurity.verify_access_token(token):
        raise AlreadyAuthenticated

    return True

async def username_already_exists(
    auth_create: AuthCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> bool:
    """
    Ensures data integrity during registration by checking if a username is already
    taken before attempting to create a new account.

    :param auth_create: The registration data containing the requested username.
    :param db: The database session for checking existing records.
    :return: False if the username is available.
    """
    user = await AuthService.get_one_by("username", auth_create.username, db)
    if user:
        raise UsernameAlreadyExists

    return False
