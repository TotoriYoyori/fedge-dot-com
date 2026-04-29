from pydantic import Field

from src.schemas import CustomBaseModel
from src.google.auth import get_google_flow
from src.google.settings import google_settings


class GoogleOAuth2FlowContext(CustomBaseModel):
    auth_url: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)
    code_verifier: str | None = Field(default=None, min_length=1)


def generate_google_oauth2_flow() -> GoogleOAuth2FlowContext:
    flow = get_google_flow()
    auth_url, state = flow.authorization_url(
        access_type=google_settings.FLOW_ACCESS_TYPE,
        include_granted_scopes=google_settings.FLOW_INCLUDE_GRANTED_SCOPES,
        prompt=google_settings.FLOW_PROMPT,
    )
    return GoogleOAuth2FlowContext(
        auth_url=auth_url,
        state=state,
        code_verifier=flow.code_verifier,
    )
