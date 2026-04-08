import datetime as dt
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr


# --------------- BASE
class DummyBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=1, max_length=64)
    dob: Optional[str] = Field(default=None, min_length=10, max_length=10)
    self_intro: Optional[str] = Field(default=None, min_length=0, max_length=255)


# --------------- WRITE SCHEMAS
class DummyCreate(DummyBase):
    """Create (POST) - email and phone are required on create"""
    email: EmailStr
    phone: str = Field(min_length=1, max_length=64)


class DummyUpdate(DummyBase):
    """Full update (PUT) — name required, everything else optional."""
    pass


class DummyPatch(DummyBase):
    """Partial update (PATCH) — every field optional, including name. """
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)


# --------------- READ SCHEMAS
class DummyResponse(DummyBase):
    id: int
    response_time: str = Field(
        default_factory=lambda: dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    model_config = ConfigDict(from_attributes=True)


class DummyDeleteResponse(BaseModel):
    id: int
    delete_time: str = Field(
        default_factory=lambda: dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    message: str = "Dummy deleted successfully."