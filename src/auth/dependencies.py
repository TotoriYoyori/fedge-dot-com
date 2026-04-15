from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import (
    AlreadyAuthenticated,
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

    async def checker(payload: Annotated[dict | None, Depends(valid_access_token_payload)]):
        if not payload:
            raise UnauthenticatedUser
        if payload.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return payload

    return checker


async def valid_access_token_payload(
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> dict | None:
    if not token:
        return None

    payload = AuthSecurity.verify_access_token(token)
    if not payload:
        raise MalformedToken

    return payload


async def valid_access_token(
    payload: Annotated[dict | None, Depends(valid_access_token_payload)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    if not payload:
        raise UnauthenticatedUser

    user_id = payload.get("sub")
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise MalformedToken

    user = await AuthService.get_one_by("id", user_id_int, db)
    if not user:
        raise UserNotFound

    return user


# --------------- EXISTENCE BOOL CHECKER (*_exists)
async def authenticated_exists(
    payload: Annotated[dict | None, Depends(valid_access_token_payload)],
) -> bool | None:
    if payload:
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
