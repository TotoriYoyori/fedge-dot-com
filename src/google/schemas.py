from datetime import datetime

from pydantic import Field

from src.schemas import CustomBaseModel


# =============== OAUTH SCHEMAS ===============
class GoogleOAuth2RedirectResponse(CustomBaseModel):
    """
    Schema for the response returned when starting the Google OAuth2 flow.

    Example:
        >>> {
        ...     "auth_url": "https://accounts.google.com/o/oauth2/auth?state=abc123",
        ...     "message": "You are being redirected to Google for authorization."
        ... }
    """

    auth_url: str
    message: str


class DebugCredentialResponse(CustomBaseModel):
    """
    Schema for a debug view of persisted Google OAuth credential data.

    Example:
        >>> {
        ...     "app_user_id": "42",
        ...     "token": "ya29.a0AfH6SM...",
        ...     "refresh_token": "1//0gExampleRefreshToken",
        ...     "token_uri": "https://oauth2.googleapis.com/token",
        ...     "client_id": "google-client-id.apps.googleusercontent.com",
        ...     "client_secret": "client-secret-value",
        ...     "scopes": "openid,email,https://www.googleapis.com/auth/gmail.readonly",
        ...     "expiry": "2026-05-04T12:30:00Z"
        ... }
    """

    app_user_id: str
    token: str | None = None
    refresh_token: str | None = None
    token_uri: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    scopes: str
    expiry: datetime | None = None


class GoogleOAuth2CredentialResponse(CustomBaseModel):
    """
    Schema for the response returned after Google OAuth credentials are stored or synced.

    Example:
        >>> {
        ...     "app_user_id": "42",
        ...     "scopes": "openid,email,https://www.googleapis.com/auth/gmail.readonly",
        ...     "expiry": "2026-05-04T12:30:00Z",
        ...     "message": "Successfully connected to Google using OAuth 2.0!"
        ... }
    """

    app_user_id: str
    scopes: str
    expiry: datetime | None = None
    message: str = "Successfully connected to Google using OAuth 2.0!"


# =============== INBOX SCHEMAS ===============
class GoogleInboxMessage(CustomBaseModel):
    """
    Schema for a single Gmail message returned from the inbox listing endpoint.

    Example:
        >>> {
        ...     "id": "196abc123def456",
        ...     "thread_id": "196abc123def000",
        ...     "subject": "Your order confirmation",
        ...     "sender": "store@example.com",
        ...     "to": "merchant@example.com",
        ...     "cc": None,
        ...     "body": "Thank you for your order.",
        ...     "date": "2026-05-03T09:15:00Z",
        ...     "date_header": "Sun, 03 May 2026 09:15:00 +0000",
        ...     "internal_date": "2026-05-03T09:15:02Z",
        ...     "label_ids": ["INBOX", "UNREAD"]
        ... }
    """

    id: str
    thread_id: str | None = Field(default=None)
    subject: str | None = Field(default=None)
    sender: str | None = Field(default=None)
    to: str | None = Field(default=None)
    cc: str | None = Field(default=None)
    body: str | None = Field(default=None)
    date: datetime | None = Field(default=None)
    date_header: str | None = Field(default=None)
    internal_date: datetime | None = Field(default=None)
    label_ids: list[str] = Field(default_factory=list)


class GoogleInboxResponse(CustomBaseModel):
    """
    Schema for the response returned when listing Gmail inbox messages.

    Example:
        >>> {
        ...     "messages": [
        ...         {
        ...             "id": "196abc123def456",
        ...             "thread_id": "196abc123def000",
        ...             "subject": "Your order confirmation",
        ...             "sender": "store@example.com",
        ...             "to": "merchant@example.com",
        ...             "cc": None,
        ...             "body": "Thank you for your order.",
        ...             "date": "2026-05-03T09:15:00Z",
        ...             "date_header": "Sun, 03 May 2026 09:15:00 +0000",
        ...             "internal_date": "2026-05-03T09:15:02Z",
        ...             "label_ids": ["INBOX", "UNREAD"]
        ...         }
        ...     ],
        ...     "result_size_estimate": 1
        ... }
    """

    messages: list[GoogleInboxMessage]
    result_size_estimate: int | None = Field(default=None)
