from datetime import datetime

from pydantic import Field

from src.schemas import CustomBaseModel


class GoogleOAuth2RedirectResponse(CustomBaseModel):
    auth_url: str
    message: str


class GoogleOAuth2NextSteps(CustomBaseModel):
    inbox: str


class GoogleOAuth2FlowContext(CustomBaseModel):
    auth_url: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)
    code_verifier: str | None = Field(default=None, min_length=1)


class GoogleCredentialResponse(CustomBaseModel):
    app_user_id: str
    email_address: str | None = None
    scopes: list[str]
    expiry: datetime | None = None


class GoogleOAuth2CallbackResponse(CustomBaseModel):
    message: str
    credential: GoogleCredentialResponse
    next_steps: GoogleOAuth2NextSteps


class GoogleInboxMessage(CustomBaseModel):
    id: str
    thread_id: str | None = Field(default=None)


class GoogleInboxResponse(CustomBaseModel):
    messages: list[GoogleInboxMessage]
    result_size_estimate: int | None = Field(default=None)
