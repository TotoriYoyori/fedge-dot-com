from datetime import datetime
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    registration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __str__(self) -> str:
        return f"Username: {self.username} | Email: {self.email} {type(self)}"

    def __repr__(self) -> str:
        return f"User(username={self.name!r}, email={self.email!r})"


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
