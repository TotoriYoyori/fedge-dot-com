from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import (
    authenticated_exists,
    username_already_exists,
    valid_access_token,
    valid_login_credentials,
)
from src.auth.models import User
from src.auth.schemas import AuthCreate, AuthResponse, Token, UserPrivate
from src.auth.security import AuthSecurity
from src.auth.service import AuthService
from src.auth.settings import auth_settings
from src.database import get_db

# --------------- ROUTER FOR USER-RELATED AUTHENTICATION
router = APIRouter(prefix="/auth", tags=["api-auth"])


@router.post(
    "/register",
    summary="Register a new user",
    description=(
        "Registers a new user into the system. It checks if the username is already taken. "
        "If a valid `role_key` is provided, the user is assigned a specific role (e.g., admin, editor), "
        "otherwise, the default role is 'user'."
    ),
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"model": AuthResponse, "description": "Successfully registered"},
        400: {"description": "Malformed input"},
        403: {"description": "Already authenticated"},
        409: {"description": "Username already exists"},
    },
    dependencies=[Depends(authenticated_exists)],
)
async def register(
    auth_create: AuthCreate,
    username_taken: Annotated[bool, Depends(username_already_exists)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User | None:
    """
    User registration flow. Expects username, email, and password.
    """
    if username_taken:
        return None

    return await AuthService.create(auth_create, db)


@router.post(
    "/login",
    summary="User login",
    description=(
        "Authenticates a user with a username and password. "
        "If successful, returns a JWT access access_token used for accessing protected resources."
    ),
    response_model=Token,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": Token, "description": "Successfully logged in"},
        401: {"description": "Invalid credentials"},
        403: {"description": "Already authenticated"},
    },
    dependencies=[Depends(authenticated_exists)],
)
async def login(
    valid_user: Annotated[User, Depends(valid_login_credentials)],
) -> Token | None:
    """
    Login endpoint. Returns Bearer access_token on success.
    """
    if not valid_user:
        return None

    access_token_expires = timedelta(minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return AuthSecurity.create_access_token(
        data={"sub": str(valid_user.id), "role": str(valid_user.role)},
        expires_delta=access_token_expires,
    )


@router.get(
    "/me",
    summary="Get current user details",
    description=(
        "Returns the detailed profile of the currently authenticated user. "
        "Requires a valid JWT access_token in the Authorization header."
    ),
    response_model=UserPrivate,
    responses={
        200: {"model": UserPrivate, "description": "Successfully retrieved user profile"},
        401: {"description": "Unauthorized access"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "User not found"},
    },
)
async def me(
    authorized_user: Annotated[User, Depends(valid_access_token)],
):
    """
    Authenticated profile endpoint.
    """
    return authorized_user
