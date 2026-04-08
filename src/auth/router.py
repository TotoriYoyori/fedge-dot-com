from fastapi import APIRouter

from .schemas import AuthenticationResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/", response_model=AuthenticationResponse)
async def login(auth: AuthenticationResponse):
    return 'Thanks for calling me'

