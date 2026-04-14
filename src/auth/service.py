import datetime as dt
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from .models import User
from .schemas import AuthCreate
from .security import AuthSecurity

# --------------- AUTHENTICATION SERVICE LAYER WITH DB
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
        role = AuthSecurity.assign_role(auth_create.role_key)

        new_user = User(
            username=auth_create.username,
            email=auth_create.email,
            password_hash=AuthSecurity.hash_password(auth_create.password),
            role=role,
            registration_date=dt.datetime.now(),
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
