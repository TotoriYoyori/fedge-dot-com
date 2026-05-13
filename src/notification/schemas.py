from datetime import datetime
from email.utils import parsedate_to_datetime
from enum import StrEnum
from typing import Annotated, Any, Optional

from fastapi import Query
from pydantic import EmailStr, Field, model_validator

from src.notification.exceptions import EmailResponseMismatch
from src.schemas import CustomBaseModel, QueryModel


# =============== ENUM SCHEMAS ===============
class EmailProviderName(StrEnum):
    """Only supports either RESEND or MAILTRAP modes."""

    RESEND = "resend"
    MAILTRAP = "mailtrap"


# =============== INPUT SCHEMAS ===============
class EmailSendPayload(CustomBaseModel):
    name: Optional[str] = None
    to_email: EmailStr
    treatment: Annotated[str, Field(min_length=1, max_length=128)] = "en eller flera behandlingar"
    location: Annotated[str, Field(min_length=1, max_length=128)] = "en av vara kliniker"
    order_number: Annotated[Optional[str], Field(description="Order number, vary per provider")] = None
    subject_line: Annotated[str, Field(min_length=1, max_length=64)] = (
        "Du har redan best\u00e4llt friskv\u00e5rdsbehandling hos oss. Boka nu!"
    )


# =============== QUERY SCHEMAS ===============
class TemplatePreviewQuery(QueryModel):
    name: Annotated[Optional[str], Query(max_length=64)] = "Cloud Strife"
    treatment: Annotated[Optional[str], Query(max_length=255)] = "en eller flera behandlingar"
    location: Annotated[Optional[str], Query(max_length=255)] = "en av vara kliniker"
    order_number: Annotated[Optional[str], Query(max_length=255)] = "order_number_123"


# =============== ADAPTER SCHEMAS ===============
class EmailProviderPayload(CustomBaseModel):
    to_email: str
    subject_line: str
    html_body: str
    plain_body: str


# =============== OUTPUT SCHEMAS ===============
class EmailSendResponse(CustomBaseModel):
    """
    App-facing adapter for email provider send responses.

    Example:
        >>> {
        ...     "id": "8a965505-63a6-4068-b4b2-d1d7da98788b",
        ...     "status": "accepted",
        ...     "accepted_at": "2026-05-12T21:51:50+00:00",
        ...     "daily_quota": 0,
        ...     "monthly_quota": 22,
        ...     "provider": "resend",
        ...     "message": "Notification email accepted for delivery.",
        ... }
    """

    id: str | None = None
    status: str = "accepted"
    accepted_at: Optional[datetime] = None
    daily_quota: Optional[int] = None
    monthly_quota: Optional[int] = None
    provider: EmailProviderName
    message: str = "Notification email accepted for delivery."

    @model_validator(mode="before")
    @classmethod
    def parse_provider_metadata(cls, data: Any) -> Any:
        payload = dict(data)
        http_headers = {key.lower(): value for key, value in payload.pop("http_headers", {}).items()}

        if payload.get("provider") != EmailProviderName.RESEND or not http_headers:
            return payload

        try:
            payload["accepted_at"] = parsedate_to_datetime(http_headers["date"])
            payload["daily_quota"] = int(http_headers["x-resend-daily-quota"])
            payload["monthly_quota"] = int(http_headers["x-resend-monthly-quota"])
        except (TypeError, ValueError, IndexError, AttributeError, KeyError) as exc:
            raise EmailResponseMismatch from exc

        return payload
