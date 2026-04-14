from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


# --------------- TESTING DUMMY MODELS
class Dummy(Base):
    __tablename__ = "dummies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(64), nullable=True)
    dob: Mapped[str] = mapped_column(String(10), nullable=True)
    self_intro: Mapped[str] = mapped_column(String(255), nullable=True)

    def __str__(self) -> str:
        return (
            f"Name: {self.name} | Email: {self.email}\n"
            f"New password hash: {self.password_hash}"
        )

    def __repr__(self) -> str:
        return (
            f"Dummy(id={self.id!r}, name={self.name!r}, "
            f"email={self.email!r}, phone={self.phone!r})"
        )
