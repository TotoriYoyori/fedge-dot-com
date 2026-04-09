from datetime import timedelta

from starlette import status
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from ..config import settings
from .schemas import AuthenticationResponse
from .models import Token
from .service import TokenPasswordService

router = APIRouter(prefix="/auth", tags=["auth"])


# @router.post(
#     "/",
#     response_model=AuthenticationResponse,
#     status_code=status.HTTP_200_OK,
# )
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     pass