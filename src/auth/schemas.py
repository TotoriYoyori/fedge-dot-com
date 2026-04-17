import datetime as dt

from pydantic import BaseModel, EmailStr, Field

from src.schemas import CustomBaseModel


# --------------- I/O SCHEMAS
class Token(BaseModel):
    """
    Schema for the authentication token response.
    """

    access_token: str = Field(
        ..., description="The JWT access token used for authorization."
    )
    token_type: str = Field(..., description="The type of the token (e.g., \"bearer\").")


class AuthCreate(CustomBaseModel):
    """
    Schema for creating a new user registration.
    """

    username: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="The unique username for the user.",
    )
    email: EmailStr = Field(..., description="The valid email address of the user.")
    password: str = Field(
        ..., min_length=8, description="The user's password (minimum 8 characters)."
    )
    role_key: str | None = Field(
        default=None,
        description="Optional special key to assign a specific role (e.g., 'admin') during registration.",
    )


class AuthResponse(CustomBaseModel):
    """
    Schema for the response sent after successful registration or login.
    """

    id: int = Field(..., description="The unique identifier of the user.")
    authentication_time: str = Field(
        default_factory=lambda: dt.datetime.now().strftime("%Y-%m-%d %H-%M-%S"),
        description="The timestamp of the authentication event.",
    )
    username: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="The username of the authenticated user.",
    )
    email: EmailStr = Field(
        ..., description="The email address of the authenticated user."
    )
    role: str = Field(
        ..., description="The role of the authenticated user (e.g., \"user\", \"admin\")."
    )


class UserPrivate(AuthResponse):
    """
    Schema for retrieving detailed private information about the current authenticated user.
    """

    message: str = Field(
        "Welcome back, master Wick ...", description="A personalized welcome message."
    )
    registration_time: dt.datetime = Field(
        ..., description="The date and time when the user registered."
    )
    password_hash: str = Field(
        min_length=8,
        description="The hashed password of the user for internal verification.",
    )
