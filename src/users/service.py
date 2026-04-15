from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User


class UserService:
    """
    Business logic for user-related operations.
    """

    @staticmethod
    async def get_all(db: AsyncSession) -> list[User]:
        stmt = select(User)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_by_id(db: AsyncSession, user_id: int) -> bool:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            await db.delete(user)
            await db.commit()
            return True
        return False
