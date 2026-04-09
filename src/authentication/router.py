from datetime import timedelta
# ----- Third Party Import
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
# ----- Local Import
from ..database import get_db
from ..config import settings
from ..dummies.schemas import DummyResponse
from .schemas import AuthenticationCreate, AuthenticationResponse
from .models import Token
from .service import AuthService

# --------------- ROUTER FOR USER-RELATED AUTHENTICATION
router = APIRouter(prefix="/authentication", tags=["authentication"])


@router.post(
    "/register",
    response_model=AuthenticationResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    new_dummy_register: AuthenticationCreate,
    db: AsyncSession = Depends(get_db)
):
    return await AuthService.create(new_dummy_register, db)
