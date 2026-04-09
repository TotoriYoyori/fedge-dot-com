from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..dummies.models import Dummy
from .security import AuthSecurity
from .models import Token
from .schemas import AuthenticationResponse, AuthenticationCreate

# --------------- AUTHENTICATION SERVICES
class AuthService:
    """
    A wrapper class for authentication-related utilities (e.g. registering and logging users in)

    Provides functions for creating new users and checking identities.

    Example usage:
        >>> hashed = AuthService.hash_password("my_secret")
    """

    # class Dummy(Base):
    #     __tablename__ = "dummies"
    #
    #     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    #     name: Mapped[str] = mapped_column(String(255), nullable=False)
    #     password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    #     email: Mapped[str] = mapped_column(String(255), nullable=True)
    #     phone: Mapped[str] = mapped_column(String(64), nullable=True)
    #     dob: Mapped[str] = mapped_column(String(10), nullable=True)
    #     self_intro: Mapped[str] = mapped_column(String(255), nullable=True)

    # class AuthenticationCreate(BaseModel):
    #     name: str = Field(min_length=1, max_length=255)
    #     email: EmailStr
    #     password: str = Field(min_length=8)

    @staticmethod
    async def create(
        new_dummy_register: AuthenticationCreate,
        db: AsyncSession
    ) -> Dummy:
        new_dummy = Dummy(
            **new_dummy_register.model_dump(exclude={'password'}),
            password_hash=AuthSecurity.hash_password(new_dummy_register.password)
        )
        db.add(new_dummy)
        await db.commit()
        await db.refresh(new_dummy)

        return new_dummy
