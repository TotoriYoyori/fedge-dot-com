import datetime as dt
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.schemas import AuthCreate
from src.auth.security import AuthSecurity


# --------------- USER DATA ACCESS SERVICES
class AuthService:
    """
    Service layer for authentication-related database operations.

    Handles user creation and retrieval with database.

    Available methods:
        - create(auth_create, db) -> User
        - get_one_by(attr: str, lookup_val: Any, db: AsyncSession) -> User | None:
        - get_many_by(attr: str, lookup_val: Any, db: AsyncSession) -> list[User] | None:
    """

    @staticmethod
    async def create(auth_create: AuthCreate, db: AsyncSession) -> User:
        """
        Create a new user in the database during registration. Returns this same user's record as response to confirm.

        Example:
            >>> sample_payload = AuthCreate(
            ...     username="john_doe",
            ...     email="john@example.com",
            ...     password="securepassword123",
            ...     role_key=None
            ... )
            >>> async def _example():
            ...     user = await AuthService.create(sample_payload, db)
            ...     return user
        """
        role = AuthSecurity.assign_role(auth_create.role_key)
        new_user = User(
            username=auth_create.username,
            email=auth_create.email,
            password_hash=AuthSecurity.hash_password(auth_create.password),
            role=role,
            registration_time=dt.datetime.now(),
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user

    @staticmethod
    async def get_one_by(attr: str, lookup_val: Any, db: AsyncSession) -> User | None:
        """
        Retrieve a single user record by a specified attribute.

        Args:
            attr (str): The column name of the User model to filter by (e.g. "username", "id").
            lookup_val (Any): The value of the above attr to match.
            db (AsyncSession): The async database session used for querying.

        Returns:
            User | None: The matching user object if found, otherwise None.

        Example:
            >>> async def _example():
            ...     await AuthService.get_one_by("username", "john_doe", db)
        """
        stmt = select(User).where(getattr(User, attr) == lookup_val)
        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_many_by(
        attr: str, lookup_val: Any, db: AsyncSession
    ) -> list[User] | None:
        """
        Same as get_one_by except returns a list of all matching user records.

        Example:
            >>> async def _example():
            ...     await AuthService.get_many_by("username", "john_doe", db)
        """
        stmt = select(User).where(getattr(User, attr) == lookup_val)
        result = await db.execute(stmt)

        return list(result.scalars().all())
