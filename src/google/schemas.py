from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GoogleCredentialResponse(BaseModel):
    app_user_id: str
    email_address: str | None = None
    scopes: list[str]
    expiry: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class GoogleInboxMessage(BaseModel):
    id: str
    thread_id: str | None = Field(default=None, alias="threadId")


class GoogleInboxResponse(BaseModel):
    messages: list[GoogleInboxMessage]
    result_size_estimate: int | None = Field(default=None, alias="resultSizeEstimate")
