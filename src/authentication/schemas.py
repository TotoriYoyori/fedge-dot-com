import datetime as dt
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class AuthenticationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8)


class AuthenticationResponse(BaseModel):
    id: int
    authentication_time: str = Field(
        default_factory=lambda: dt.datetime.now().strftime("%Y-%m-%d %H-%M-%S"),
    )
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password_hash: str = Field(min_length=8)

    model_config = ConfigDict(from_attributes=True)
