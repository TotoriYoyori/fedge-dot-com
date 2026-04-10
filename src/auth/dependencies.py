from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from oauthlib.oauth2.rfc8628.errors import ExpiredTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ..database import get_db
from .exceptions import (
    UnauthenticatedUser,
    UsernameAlreadyExists,
    MalformedToken,
    UserNotFound
)
from .security import AuthSecurity, oauth2_scheme
from .schemas import AuthCreate
from .service import AuthService
from .models import User

# --------------- ACTUAL USER AUTHENTICATION DEPENDENCIES
async def username_already_exists(
    auth_create: AuthCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> bool:
    user = await AuthService.get_one_by("username", auth_create.username, db)
    if user:
        raise UsernameAlreadyExists

    return False


async def valid_login_credentials(
    login_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    user = await AuthService.get_one_by("username", login_form.username, db)
    if not user or not AuthSecurity.verify_password(login_form.password, user.password_hash):
        raise UnauthenticatedUser

    return user


async def valid_access_token(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> int:
    user_id  = AuthSecurity.verify_access_token(token)
    if not user_id:
        raise ExpiredTokenError

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise MalformedToken
    else:
        return user_id_int


async def valid_user_id(
    token_user_id: Annotated[int, Depends(valid_access_token)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    user = await AuthService.get_one_by("id", token_user_id, db)
    if not user:
        raise UserNotFound

    return user

# --------------- LEGACY TESTING
async def dummy_with_name_exists(
    authentication_create: AuthCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> bool:
    dummy = await AuthService.get_by_name(authentication_create.name, db)
    if dummy:
        raise DummyNameAlreadyExists

    return False
