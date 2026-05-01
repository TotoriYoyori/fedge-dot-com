from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
from base64 import urlsafe_b64decode
from html.parser import HTMLParser

import asyncer
from google.oauth2.credentials import Credentials
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.google.models import GoogleOAuthCredential, GoogleOAuthState
from src.google.security import GoogleOAuthCredentialRecord, GoogleOAuthSecurity
from src.google.schemas import (
    GoogleOAuth2CredentialResponse,
    GoogleOAuth2RedirectResponse
)


# --------------- USE CASES (ORCHESTRATOR OF SERVICES AND SECURITY)
async def initiate_oauth2(db: AsyncSession, valid_user: User) -> GoogleOAuth2RedirectResponse:
    """Connect with Google, persist the connection state in DB, and return redirect payload.

    Args:
        db: Active async database session used to persist the OAuth state.
        valid_user: Authenticated application user starting the OAuth flow.

    Returns:
        GoogleOAuth2RedirectResponse: Redirect data containing the Google
        authorization URL and a user-facing message.

    Example:
        >>> async def run_example() -> str:
        ...     response = await initiate_oauth2(db, valid_user)
        ...     return response.auth_url
    """
    auth_url, state, code_verifier = GoogleOAuthSecurity.init_flow()

    await GoogleOAuthService.create_state(
        db=db,
        valid_user=valid_user,
        state=state,
        code_verifier=code_verifier,
    )
    return GoogleOAuth2RedirectResponse(
        auth_url=auth_url,
        message="You are being redirected to Google for authorization.",
    )


async def exchange_code_for_credentials(
    db: AsyncSession,
    exchange_code: str,
    oauth_state: GoogleOAuthState,
) -> GoogleOAuth2CredentialResponse:
    """Exchange callback code, persist base credentials, and consume the OAuth state.

    Args:
        db: Active async database session used for state consumption and credential persistence.
        exchange_code: Authorization code returned by Google's OAuth2 callback.
        oauth_state: Persisted OAuth state new_record containing the app user id and PKCE verifier.

    Returns:
        GoogleOAuth2CredentialResponse: Public callback response for the connected Google account.

    Example:
        >>> async def run_example() -> str:
        ...     response = await exchange_code_for_credentials(db, exchange_code, oauth_state)
        ...     return response.app_user_id
    """
    credentials = await GoogleOAuthSecurity.pkce_flow(exchange_code, oauth_state)
    new_record = GoogleOAuthSecurity.build_app_oauth_credential(
        credentials,
        oauth_state.app_user_id
    )
    existing_record = await GoogleOAuthService.get_credential(
        db,
        oauth_state.app_user_id,
    )
    if existing_record is None:
        await GoogleOAuthService.create_oauth_credential(db, new_record, oauth_state)
    else:
        await GoogleOAuthService.update_oauth_credential(db, existing_record, new_record, oauth_state)

    return GoogleOAuth2CredentialResponse(
        app_user_id=new_record.app_user_id,
        scopes=new_record.scopes,
        expiry=new_record.expiry,
    )


async def connect_gmail_service(
    db: AsyncSession,
    record: GoogleOAuthCredential,
) -> GoogleOAuth2CredentialResponse:
    record = await refresh_credential_if_needed(db, record)
    credentials = GoogleOAuthSecurity.build_google_credentials(record)
    credentials.expiry = record.expiry

    email_address = await GoogleOAuthSecurity.get_authorized_email(credentials)
    record = await GoogleOAuthService.sync_gmail_profile(db, record, email_address)

    return GoogleOAuth2CredentialResponse(
        app_user_id=record.app_user_id,
        scopes=record.scopes,
        expiry=record.expiry,
    )


async def list_gmail_inbox(
    db: AsyncSession,
    record: GoogleOAuthCredential,
    max_results: int,
    sender: str | None = None,
    label: str | None = None,
    after: date | None = None,
    before: date | None = None,
) -> dict:
    record = await refresh_credential_if_needed(db, record)
    service = GoogleOAuthSecurity.create_gmail_service(record)
    gmail_query = _build_gmail_inbox_query(
        sender=sender,
        label=label,
        after=after,
        before=before,
    )

    results = await asyncer.asyncify(
        lambda: service.users().messages().list(
            userId="me",
            maxResults=max_results,
            q=gmail_query,
        ).execute()
    )()

    # --------------- EMAIL PARSING / ENRICHMENT (REFactor boundary)
    # FIXME: Move inbox message enrichment behind a dedicated parser/service layer.
    # The current implementation mixes listing, per-message fetches, and response
    # shaping inside one function, which should be split before this grows further.
    message_refs = results.get("messages", [])
    message_details = await asyncer.asyncify(
        lambda: [
            service.users().messages().get(
                userId="me",
                id=message["id"],
                format="full",
            ).execute()
            for message in message_refs
        ]
    )()
    # --------------- END EMAIL PARSING / ENRICHMENT

    return {
        "messages": [_serialize_gmail_message(message) for message in message_details],
        "result_size_estimate": results.get("resultSizeEstimate"),
    }


def _serialize_gmail_message(message: dict) -> dict:
    headers = _extract_gmail_headers(message.get("payload", {}).get("headers", []))
    date_header = headers.get("date")

    return {
        "id": message["id"],
        "thread_id": message.get("threadId"),
        "subject": headers.get("subject"),
        "sender": headers.get("from"),
        "to": headers.get("to"),
        "cc": headers.get("cc"),
        "body": _extract_gmail_body_text(message.get("payload", {})),
        "date": _parse_gmail_date_header(date_header),
        "date_header": date_header,
        "internal_date": _parse_gmail_internal_date(message.get("internalDate")),
        "label_ids": message.get("labelIds", []),
    }


def _build_gmail_inbox_query(
    sender: str | None,
    label: str | None,
    after: date | None,
    before: date | None,
) -> str | None:
    query_parts: list[str] = []

    if sender:
        query_parts.append(f"from:{sender.strip()}")
    if label:
        query_parts.append(f"label:{label.strip()}")
    if after:
        query_parts.append(f"after:{after.isoformat()}")
    if before:
        query_parts.append(f"before:{before.isoformat()}")

    return " ".join(query_parts) or None


def _extract_gmail_headers(headers: list[dict]) -> dict[str, str]:
    return {
        header["name"].lower(): header["value"]
        for header in headers
        if header.get("name") and header.get("value")
    }


def _extract_gmail_body_text(payload: dict) -> str | None:
    plain_text = _find_gmail_body_by_mime_type(payload, "text/plain")
    if plain_text:
        return plain_text

    html_text = _find_gmail_body_by_mime_type(payload, "text/html")
    if html_text:
        return _strip_html(html_text)

    return _decode_gmail_body_data(payload.get("body", {}).get("data"))


def _find_gmail_body_by_mime_type(payload: dict, mime_type: str) -> str | None:
    if payload.get("mimeType") == mime_type:
        decoded = _decode_gmail_body_data(payload.get("body", {}).get("data"))
        if decoded:
            return decoded

    for part in payload.get("parts", []):
        decoded = _find_gmail_body_by_mime_type(part, mime_type)
        if decoded:
            return decoded

    return None


def _decode_gmail_body_data(body_data: str | None) -> str | None:
    if not body_data:
        return None

    padding = "=" * (-len(body_data) % 4)
    try:
        decoded_bytes = urlsafe_b64decode(f"{body_data}{padding}")
    except (ValueError, TypeError):
        return None

    try:
        return decoded_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return decoded_bytes.decode("latin-1", errors="replace")


def _strip_html(html_content: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(html_content)
    parser.close()
    return parser.get_text()


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self._chunks.append(data.strip())

    def get_text(self) -> str:
        return "\n".join(self._chunks).strip()


def _parse_gmail_date_header(date_header: str | None) -> datetime | None:
    if not date_header:
        return None

    try:
        parsed = parsedate_to_datetime(date_header)
    except (TypeError, ValueError, IndexError):
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)

    return parsed


def _parse_gmail_internal_date(internal_date: str | None) -> datetime | None:
    if not internal_date:
        return None

    try:
        return datetime.fromtimestamp(int(internal_date) / 1000, tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        return None


# --------------- CRUD SERVICES
class GoogleOAuthService:

    @staticmethod
    async def create_state(
        db: AsyncSession,
        valid_user: User,
        state: str,
        code_verifier: str | None,
    ) -> GoogleOAuthState:
        new_oauth_state = GoogleOAuthState(
            state=state,
            app_user_id=str(valid_user.id),
            code_verifier=code_verifier,
            created_time=datetime.now(timezone.utc),
        )
        db.add(new_oauth_state)

        await db.commit()
        await db.refresh(new_oauth_state)

        return new_oauth_state

    @staticmethod
    async def get_state(db: AsyncSession, state: str) -> GoogleOAuthState:
        result = await db.execute(
            select(GoogleOAuthState).where(GoogleOAuthState.state == state)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_state(db: AsyncSession, oauth_state: GoogleOAuthState) -> None:
        await db.delete(oauth_state)
        await db.commit()

    @staticmethod
    async def create_oauth_credential(
        db: AsyncSession,
        new_record: GoogleOAuthCredentialRecord,
        oauth_state: GoogleOAuthState,
    ) -> GoogleOAuthCredential:
        payload_data = new_record.model_dump()
        now = datetime.now(timezone.utc)
        new_record = GoogleOAuthCredential(
            **payload_data,
            created_time=now,
            updated_time=now,
        )
        db.add(new_record)
        await db.delete(oauth_state)

        await db.commit()
        await db.refresh(new_record)

        return new_record

    @staticmethod
    async def update_oauth_credential(
        db: AsyncSession,
        new_record: GoogleOAuthCredential,
        existing_record: GoogleOAuthCredentialRecord,
        oauth_state: GoogleOAuthState,
    ) -> GoogleOAuthCredential:
        payload_data = existing_record.model_dump()
        payload_data["refresh_token"] = (
            existing_record.refresh_token or new_record.refresh_token
        )
        for field_name, field_value in payload_data.items():
            setattr(new_record, field_name, field_value)

        new_record.updated_time = datetime.now(timezone.utc)

        await db.delete(oauth_state)
        await db.commit()
        await db.refresh(new_record)

        return new_record

    @staticmethod
    async def get_credential(
        db: AsyncSession,
        app_user_id: str,
    ) -> GoogleOAuthCredential | None:
        result = await db.execute(
            select(GoogleOAuthCredential).where(
                GoogleOAuthCredential.app_user_id == app_user_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def upsert_credential(
        db: AsyncSession,
        record: GoogleOAuthCredential,
        credentials: Credentials,
        email_address: str | None = None,
    ) -> GoogleOAuthCredential:
        record.access_token = credentials.token
        record.refresh_token = credentials.refresh_token or record.refresh_token
        record.token_uri = credentials.token_uri or record.token_uri
        record.client_id = credentials.client_id or record.client_id
        record.client_secret = credentials.client_secret or record.client_secret
        record.scopes = ",".join(credentials.scopes or []) or record.scopes
        record.expiry = credentials.expiry
        record.email_address = email_address or record.email_address
        record.updated_time = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(record)

        return record

    @staticmethod
    async def sync_gmail_profile(
        db: AsyncSession,
        record: GoogleOAuthCredential,
        email_address: str | None,
    ) -> GoogleOAuthCredential:
        record.email_address = email_address or record.email_address
        record.updated_time = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(record)

        return record


async def refresh_credential_if_needed(
    db: AsyncSession,
    record: GoogleOAuthCredential,
) -> GoogleOAuthCredential:
    creds = GoogleOAuthSecurity.build_google_credentials(record)
    creds.expiry = record.expiry

    if creds.expired and creds.refresh_token:
        await GoogleOAuthSecurity.refresh_credentials(creds)
        await GoogleOAuthService.upsert_credential(
            db=db,
            record=record,
            credentials=creds,
            email_address=record.email_address,
        )
        refreshed = await GoogleOAuthService.get_credential(db, record.app_user_id)
        if refreshed is not None:
            return refreshed

    return record


async def ensure_google_oauth_schema(db: AsyncSession) -> None:
    state_columns = await db.execute(text("PRAGMA table_info(google_oauth_states)"))
    state_column_names = {row[1] for row in state_columns.fetchall()}
    if "code_verifier" not in state_column_names:
        await db.execute(
            text("ALTER TABLE google_oauth_states ADD COLUMN code_verifier TEXT")
        )
        await db.commit()
