from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dummies.dependencies import dummy_with_name_exists
from .schemas import AuthenticationCreate, AuthenticationResponse
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
    dummy_already_exists: bool = Depends(dummy_with_name_exists),
    db: AsyncSession = Depends(get_db)
):
    if dummy_already_exists:
        return None

    return await AuthService.create(new_dummy_register, db)
