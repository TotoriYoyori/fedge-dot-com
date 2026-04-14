from datetime import datetime

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


# --------------- OFFICIAL FEDGE USERS MODEL
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="user")
    registration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __str__(self) -> str:
        return f"Username: {self.username} | Email: {self.email} {type(self)}"

    def __repr__(self) -> str:
        return f"User(username={self.name!r}, email={self.email!r})"
