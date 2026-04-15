from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import (
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


def require_role(*roles: str):
    """
    A role-based access control dependency factory.

    Checks if the authenticated user has one of the required roles.
    Raises HTTPException 403 if the user doesn't have the necessary permissions.
    """

    async def checker(current_user: Annotated[User, Depends(valid_access_token)]):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return checker


async def valid_access_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    user_id = AuthSecurity.verify_access_token(token)
    if not user_id:
        raise MalformedToken

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise MalformedToken

    user = await AuthService.get_one_by("id", user_id_int, db)
    if not user:
        raise UserNotFound

    return user


# --------------- EXISTENCE BOOL CHECKER (*_exists)
async def username_already_exists(
    auth_create: AuthCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> bool:
    user = await AuthService.get_one_by("username", auth_create.username, db)
    if user:
        raise UsernameAlreadyExists

    return False
