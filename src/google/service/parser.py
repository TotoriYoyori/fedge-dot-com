from base64 import urlsafe_b64decode
from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser

import asyncer
from sqlalchemy.ext.asyncio import AsyncSession

from src.google.models import GoogleOAuthCredential

from src.google.service.client import create_gmail_service
from src.google.service.flow import refresh_credential_if_needed


# =============== INBOX FETCH ===============
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
    service = create_gmail_service(record)
    gmail_query = _build_gmail_inbox_query(
        sender=sender,
        label=label,
        after=after,
        before=before,
    )

    results = await asyncer.asyncify(
        lambda: service.users()
        .messages()
        .list(
            userId="me",
            maxResults=max_results,
            q=gmail_query,
        )
        .execute()
    )()

    message_refs = results.get("messages", [])
    message_details = await asyncer.asyncify(
        lambda: [
            service.users()
            .messages()
            .get(
                userId="me",
                id=message["id"],
                format="full",
            )
            .execute()
            for message in message_refs
        ]
    )()

    return {
        "messages": [_serialize_gmail_message(message) for message in message_details],
        "result_size_estimate": results.get("resultSizeEstimate"),
    }


# =============== MESSAGE PARSING ===============
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


# =============== BODY PARSING ===============
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


# =============== HTML PARSING ===============
class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self._chunks.append(data.strip())

    def get_text(self) -> str:
        return "\n".join(self._chunks).strip()


# =============== DATE PARSING ===============
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
