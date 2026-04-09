from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..config import settings
from ..database import get_db
from ..dummies.schemas import DummyPrivate
from .dependencies import dummy_with_name_exists, valid_login_credentials
from .schemas import AuthenticationCreate, AuthenticationResponse, Token
from .security import AuthSecurity, oauth2_scheme
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


@router.get("/me", response_model=DummyPrivate)
async def me(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get the currently authenticated dummy.
    """
    dummy_id  = AuthSecurity.verify_access_token(token)
    if not dummy_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        dummy_id_int = int(dummy_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    stmt = select(Dummy).where(Dummy.id == dummy_id_int)
    result = await db.execute(stmt)
    dummy = result.scalar_one_or_none()
    if not dummy:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not identifiable by token",
            header={"WWW-Authenticate": "Bearer"}
        )

    return dummy
