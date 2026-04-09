# ----- Dependencies Import
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

# ----- App Modules
from ..database import Base


# --------------- FAKE-USERS-RELATED ORM MODELS
class Dummy(Base):
    __tablename__ = "dummies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(64), nullable=True)
    dob: Mapped[str] = mapped_column(String(10), nullable=True)
    self_intro: Mapped[str] = mapped_column(String(255), nullable=True)

    def __str__(self):
        return (
            f"{self.name} | {self.email}\n"
            f"New password hash: {self.password_hash}"
        )
        return (
            f"{self.name} | {self.email} | {self.phone} | {self.dob}\n"
            f"{self.self_intro}\n"
            f"{type(self)}"
        )

    def __repr__(self) -> str:
        return (
            f"Dummy(id={self.id!r}, name={self.name!r}, "
            f"email={self.email!r}, phone={self.phone!r})"
        )
