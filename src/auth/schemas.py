import datetime as dt
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class AuthCreate(BaseModel):
    """
    User must input a name, email, and password to register as a new user.
    """
    username: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)


class AuthResponse(BaseModel):
    """
    Server response back to users upon successful login or registration.
    """
    id: int
    authentication_time: str = Field(
        default_factory=lambda: dt.datetime.now().strftime("%Y-%m-%d %H-%M-%S"),
    )
    username: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password_hash: str = Field(min_length=8)

    model_config = ConfigDict(from_attributes=True)


class UserPrivate(AuthResponse):
    message: str = 'Welcome back, master Wick ...'
    registration_date: dt.datetime
    password_hash: str = Field(min_length=8)


class Token(BaseModel):
    """
    Server returns an access token back to users upon successful login or registration.
    """
    access_token: str
    token_type: str
