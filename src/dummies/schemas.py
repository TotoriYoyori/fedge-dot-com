import datetime as dt
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr


# --------------- WRITE SCHEMAS
class DummyWrite(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=1, max_length=64)
    dob: Optional[str] = Field(default=None, min_length=10, max_length=10)
    self_intro: Optional[str] = Field(default=None, min_length=0, max_length=255)


class DummyCreate(DummyWrite):
    """Create (POST) - email, phone, and password are required on create"""
    email: EmailStr
    phone: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=8)


class DummyUpdate(DummyWrite):
    """Full update (PUT) — name required, everything else optional."""
    pass


class DummyPatch(DummyWrite):
    """Partial update (PATCH) — every field optional, including name. """
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)


# --------------- READ / RESPONSE SCHEMAS
class DummyResponse(BaseModel):
    id: int
    response_time: str = Field(
        default_factory=lambda: dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    name: str = Field(min_length=1, max_length=255)
    dob: Optional[str] = Field(default=None, min_length=10, max_length=10)
    self_intro: Optional[str] = Field(default=None, min_length=0, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=1, max_length=64)

    model_config = ConfigDict(from_attributes=True)


class DummyPrivateResponse(DummyResponse):
    pass


class DummyDeleteResponse(BaseModel):
    id: int
    delete_time: str = Field(
        default_factory=lambda: dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    message: str = "Dummy deleted successfully."
