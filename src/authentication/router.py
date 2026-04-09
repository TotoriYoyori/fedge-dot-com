from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from .dependencies import dummy_with_name_exists, valid_login_credentials
from .schemas import AuthenticationCreate, AuthenticationResponse, Token
from .security import AuthSecurity
from .service import AuthService
from .models import Dummy

# --------------- ROUTER FOR USER-RELATED AUTHENTICATION
router = APIRouter(prefix="/authentication", tags=["authentication"])


@router.post(
    "/register",
    response_model=AuthenticationResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    authentication_create: AuthenticationCreate,
    dummy_already_exists: bool = Depends(dummy_with_name_exists),
    db: AsyncSession = Depends(get_db)
):
    if dummy_already_exists:
        return None

    return await AuthService.create(authentication_create, db)


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK
)
async def login(
    login_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    dummy_logging_in: Annotated[Dummy, Depends(valid_login_credentials)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Verify and authenticate the user's name and password.
    """
    if not dummy_logging_in:
        return None

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return AuthSecurity.create_access_token(
        data={"sub": str(dummy_logging_in.id)},
        expires_delta=access_token_expires,
    )
