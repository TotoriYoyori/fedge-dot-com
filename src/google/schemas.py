from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


from src.schemas import CustomBaseModel


class GoogleCredentialResponse(CustomBaseModel):
    app_user_id: str
    email_address: str | None = None
    scopes: list[str]
    expiry: datetime | None = None


class GoogleInboxMessage(CustomBaseModel):
    id: str
    thread_id: str | None = Field(default=None)


class GoogleInboxResponse(CustomBaseModel):
    messages: list[GoogleInboxMessage]
    result_size_estimate: int | None = Field(default=None)
