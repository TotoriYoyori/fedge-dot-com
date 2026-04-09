from sqlalchemy.ext.asyncio import AsyncSession

from ..dummies.models import Dummy
from .security import AuthSecurity
from .schemas import AuthenticationCreate


class AuthService:
    """
    A wrapper class for authentication-related utilities (e.g. registering and logging users in)

    Provides functions for creating new users and checking identities.

    Example usage:
        >>> hashed = AuthService.create_dummy(new_dummy, db)
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
