from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from .dependencies import (
    username_already_exists,
    valid_access_token,
    valid_login_credentials,
)
from .models import User
from .schemas import AuthCreate, AuthResponse, Token, UserPrivate
from .security import AuthSecurity
from .service import AuthService

# --------------- ROUTER FOR USER-RELATED AUTHENTICATION
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    summary="Register a new user",
    description=(
        "Registers a new user into the system. It checks if the username is already taken. "
        "If a valid `role_key` is provided, the user is assigned a specific role (e.g., admin, editor), "
        "otherwise, the default role is 'user'."
    ),
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    auth_create: AuthCreate,
    username_taken: Annotated[bool, Depends(username_already_exists)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> AuthResponse | None:
    """
    User registration flow. Expects username, email, and password.
    """
    if username_taken:
        return None

    return await AuthService.create(auth_create, db)

# TotoriYoyori / mastercode123
@router.post(
    "/login",
    summary="User login",
    description=(
        "Authenticates a user with a username and password. "
        "If successful, returns a JWT access token used for accessing protected resources."
    ),
    response_model=Token,
    status_code=status.HTTP_200_OK
)
async def login(
    valid_user: Annotated[User, Depends(valid_login_credentials)]
) -> Token | None:
    """
    Login endpoint. Returns Bearer token on success.
    """
    if not valid_user:
        return None

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return AuthSecurity.create_access_token(
        data={"sub": str(valid_user.id)},
        expires_delta=access_token_expires,
    )


@router.get(
    "/me",
    summary="Get current user details",
    description=(
        "Returns the detailed profile of the currently authenticated user. "
        "Requires a valid JWT token in the Authorization header."
    ),
    response_model=UserPrivate
)
async def me(
    authorized_user: Annotated[User, Depends(valid_access_token)],
):
    """
    Authenticated profile endpoint.
    """
    return authorized_user
