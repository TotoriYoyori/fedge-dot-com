from typing import Annotated, Callable

from fastapi import Depends
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


# --------------- ORM-RETURNING VALIDATION (valid_*)
async def valid_login_credentials(
    login_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
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
    if not token:
        raise UnauthenticatedUser

    payload = AuthSecurity.verify_access_token(token)
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


def require_role(*roles: str) -> Callable:
    """
    A role-based access control dependency factory.

    Checks if the authenticated user has one of the required roles.
    Raises InsufficientPermission if the user doesn't have the necessary permissions.
    """
    async def checker(user: Annotated[User, Depends(valid_access_token)]) -> User:
        if user.role not in roles:
            raise InsufficientPermission

        return user

    return checker


# --------------- EXISTENCE BOOL CHECKER (*_exists)
async def authenticated_exists(
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> bool | None:
    if token and AuthSecurity.verify_access_token(token):
        raise AlreadyAuthenticated

    return True

async def username_already_exists(
    auth_create: AuthCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> bool:
    user = await AuthService.get_one_by("username", auth_create.username, db)
    if user:
        raise UsernameAlreadyExists

    return False
