from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Dummy
from .security import AuthSecurity
from .schemas import AuthenticationCreate


class AuthService:
    """
    A wrapper class for authentication-related utilities (e.g. registering and logging users in)

    Provides functions for creating new users and checking identities.

    Example usage:
        >>> async def register():
        >>>     return await AuthService.create(authentication_create, db)
    """
    @staticmethod
    async def create(authentication_create: AuthenticationCreate, db: AsyncSession) -> Dummy:
        new_dummy = Dummy(
            **authentication_create.model_dump(exclude={"password"}),
            password_hash=AuthSecurity.hash_password(authentication_create.password),
        )
        db.add(new_dummy)
        await db.commit()
        await db.refresh(new_dummy)

        return new_dummy

    @staticmethod
    async def get_by_name(dummy_name: str, db: AsyncSession) -> Dummy | None:
        stmt = select(Dummy).where(func.lower(Dummy.name) == dummy_name.lower())
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
