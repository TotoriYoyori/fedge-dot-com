from src.auth.schemas import AuthResponse
from src.schemas import CustomBaseModel


class UserPublic(AuthResponse):
    """
    Public profile information for a user.
    """

    pass


class UserCreate(CustomBaseModel):
    """
    Schema for creating a user (internal use).
    """

    pass


class UserUpdate(CustomBaseModel):
    """
    Schema for updating user details.
    """

    pass
