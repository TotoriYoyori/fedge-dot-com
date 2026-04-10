import datetime as dt
from typing import Any
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, Dummy
from .security import AuthSecurity
from .schemas import AuthCreate


class AuthService:
    """
    A wrapper class for authentication-related utilities (e.g. registering and logging users in).

    Provides functions for creating new users and checking identities.

    Example usage:
        >>> async def register():
        >>>     return await AuthService.create(auth_create, db)
    """
    @staticmethod
    async def create(auth_create: AuthCreate, db: AsyncSession) -> User:
        new_user = User(
            **auth_create.model_dump(exclude={"password"}),
            registration_date=dt.datetime.now(),
            password_hash=AuthSecurity.hash_password(auth_create.password),
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user

    @staticmethod
    async def get_one_by(
        attr: str,
        lookup_val: Any,
        db: AsyncSession
    ) -> User | None:
        stmt = select(User).where(getattr(User, attr) == lookup_val)
        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_many_by(
        attr: str,
        lookup_val: Any,
        db: AsyncSession
    ) -> list[User] | None:
        stmt = select(User).where(getattr(User, attr) == lookup_val)
        result = await db.execute(stmt)

        return result.scalars().all()


    # --------------- ONLY FOR DUMMIES
    @staticmethod
    async def get_by_name(dummy_name: str, db: AsyncSession) -> Dummy | None:
        """LEGACY! Only for dummies"""
        stmt = select(Dummy).where(func.lower(Dummy.name) == dummy_name.lower())
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
