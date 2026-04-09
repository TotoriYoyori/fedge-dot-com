from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from .exceptions import DummyNameAlreadyExists, UnauthenticatedDummy
from .security import AuthSecurity
from .schemas import AuthenticationCreate
from .service import AuthService
from .models import Dummy

async def dummy_with_name_exists(
    authentication_create: AuthenticationCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> bool:
    dummy = await AuthService.get_by_name(authentication_create.name, db)
    if dummy:
        raise DummyNameAlreadyExists

    return False


async def valid_login_credentials(
    login_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Dummy:
    dummy = await AuthService.get_by_name(login_form.username, db)
    if not dummy or not AuthSecurity.verify_password(login_form.password, dummy.password_hash):
        raise UnauthenticatedDummy

    return dummy
