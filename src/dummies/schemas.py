from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class DummyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=64)


class DummyResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
