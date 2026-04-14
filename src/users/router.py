from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.models import User
from ..database import get_db


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
async def get_all_users(
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User)
    result = await db.execute(stmt)

    return result.scalars().all()


@router.delete(
    "/{user_id}",
    response_model=None,
)
async def delete_users(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)

    print(result.scalar_one_or_none())
