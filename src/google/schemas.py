from datetime import datetime

from pydantic import Field

from src.schemas import CustomBaseModel


class GoogleOAuth2RedirectResponse(CustomBaseModel):
    auth_url: str
    message: str


class DebugCredentialResponse(CustomBaseModel):
    app_user_id: str
    token: str | None = None
    refresh_token: str | None = None
    token_uri: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    scopes: str
    expiry: datetime | None = None


class GoogleOAuth2CredentialResponse(CustomBaseModel):
    app_user_id: str
    scopes: str
    expiry: datetime | None = None
    message: str = "Successfully connected to Google using OAuth 2.0!"


class GoogleInboxMessage(CustomBaseModel):
    id: str
    thread_id: str | None = Field(default=None)
    subject: str | None = Field(default=None)
    sender: str | None = Field(default=None)
    to: str | None = Field(default=None)
    cc: str | None = Field(default=None)
    snippet: str | None = Field(default=None)
    date: datetime | None = Field(default=None)
    date_header: str | None = Field(default=None)
    internal_date: datetime | None = Field(default=None)
    label_ids: list[str] = Field(default_factory=list)


class GoogleInboxResponse(CustomBaseModel):
    messages: list[GoogleInboxMessage]
    result_size_estimate: int | None = Field(default=None)
