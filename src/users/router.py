from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import require_role
from src.database import get_db
from src.users.schemas import UserPublic
from src.users.service import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(require_role("admin"))],
)


@router.get(
    "/",
    response_model=list[UserPublic],
    status_code=status.HTTP_200_OK,
    summary="Get all users",
)
async def get_all_users(db: AsyncSession = Depends(get_db)) -> list[UserPublic]:
    """
    Returns a list of all users in the system.
    """
    return await UserService.get_all(db)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> None:
    """
    Deletes a user by their ID.
    """
    await UserService.delete_by_id(db, user_id)
