from datetime import UTC, datetime

from pydantic import Field

from src.schemas import CustomBaseModel


# =============== OAUTH SCHEMAS ===============
class GoogleOAuth2StateCreate(CustomBaseModel):
    """
    Schema for the app-side payload used to create a Google OAuth state record.

    Example:
        >>> {
        ...     "state": "abc123state",
        ...     "auth_url": "https://accounts.google.com/o/oauth2/auth?state=abc123state",
        ...     "user_id": 42,
        ...     "code_verifier": "pkce-code-verifier-value",
        ...     "created_time": "2026-05-04T12:45:00Z"
        ... }
    """

    state: str
    auth_url: str
    user_id: int
    code_verifier: str
    created_time: datetime = Field(default_factory=lambda: datetime.now(UTC))


class GoogleOAuth2CredentialCreate(CustomBaseModel):
    """
    Schema for the app-side payload used to create or update Google OAuth credentials.

    Example:
        >>> {
        ...     "user_id": 42,
        ...     "access_token": "ya29.a0AfH6SMExample",
        ...     "refresh_token": "1//0gExampleRefreshToken",
        ...     "token_uri": "https://oauth2.googleapis.com/token",
        ...     "client_id": "google-client-id.apps.googleusercontent.com",
        ...     "client_secret": "client-secret-value",
        ...     "scopes": "openid,email,https://www.googleapis.com/auth/gmail.readonly",
        ...     "expiry": "2026-05-04T12:30:00Z",
        ...     "email_address": "merchant@example.com"
        ... }
    """

    user_id: int
    access_token: str
    refresh_token: str | None = None
    token_uri: str
    client_id: str
    client_secret: str
    scopes: str
    expiry: datetime | None = None
    email_address: str | None = None
    created_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_time: datetime = Field(default_factory=lambda: datetime.now(UTC))


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
    message: str = "You are being redirected to Google for authorization."


class DebugCredentialResponse(CustomBaseModel):
    """
    Schema for a debug view of persisted Google OAuth credential data.

    Example:
        >>> {
        ...     "user_id": 42,
        ...     "token": "ya29.a0AfH6SM...",
        ...     "refresh_token": "1//0gExampleRefreshToken",
        ...     "token_uri": "https://oauth2.googleapis.com/token",
        ...     "client_id": "google-client-id.apps.googleusercontent.com",
        ...     "client_secret": "client-secret-value",
        ...     "scopes": "openid,email,https://www.googleapis.com/auth/gmail.readonly",
        ...     "expiry": "2026-05-04T12:30:00Z"
        ... }
    """

    user_id: int
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
        ...     "user_id": 42,
        ...     "scopes": "openid,email,https://www.googleapis.com/auth/gmail.readonly",
        ...     "expiry": "2026-05-04T12:30:00Z",
        ...     "message": "Successfully connected to Google using OAuth 2.0!"
        ... }
    """

    user_id: int
    scopes: str
    expiry: datetime | None = None
    message: str = "Successfully connected to Google using OAuth 2.0!"


# =============== INBOX SCHEMAS ===============
class GmailMessageResponse(CustomBaseModel):
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


class GmailInboxResponse(CustomBaseModel):
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

    messages: list[GmailMessageResponse]
    result_size_estimate: int | None = Field(default=None)
