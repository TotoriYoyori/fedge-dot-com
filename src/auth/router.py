from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..config import settings
from ..database import get_db
from .schemas import UserPrivate
from .dependencies import (
    valid_login_credentials,
    username_already_exists,
    valid_access_token,
    valid_user_id
)
from .schemas import AuthCreate, AuthResponse, Token
from .security import AuthSecurity, oauth2_scheme
from .service import AuthService
from .models import Dummy

# --------------- ROUTER FOR USER-RELATED AUTHENTICATION
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    auth_create: AuthCreate,
    username_taken: Annotated[bool, Depends(username_already_exists)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Register a new user to Fedge's Service. Request body (AuthCreate) contains a username, email, and password.
    """
    if username_taken:
        return None

    return await AuthService.create(auth_create, db)

# TotoriYoyori / mastercode123
@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK
)
async def login(
    valid_user: Annotated[Dummy, Depends(valid_login_credentials)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Verify and authenticate the username and password.
    """
    if not valid_user:
        return None

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return AuthSecurity.create_access_token(
        data={"sub": str(valid_user.id)},
        expires_delta=access_token_expires,
    )


@router.get("/me", response_model=UserPrivate)
async def me(
    valid_token_user_id: Annotated[int, Depends(valid_access_token)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get the currently authenticated dummy.
    """
    return await AuthService.get_one_by("id", valid_token_user_id, db)
