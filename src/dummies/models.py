# ----- Dependencies Import
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

# ----- App Modules
from src.database import Base

# --------------- USERS-RELATED ORM MODELS
class Dummy(Base):
    __tablename__ = "dummies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(64), nullable=True)

    def __str__(self):
        return f"{self.name} | {self.email} | {self.phone} {type(self)}"

    def __repr__(self) -> str:
        return (
            f"Dummy(id={self.id!r}, name={self.name!r}, "
            f"email={self.email!r}, phone={self.phone!r})"
        )
