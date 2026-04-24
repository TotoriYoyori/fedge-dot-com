import datetime as dt
from typing import Dict, Optional

from pydantic import EmailStr, Field

from src.schemas import CustomBaseModel


class TemplateFormat(CustomBaseModel):
    name: Optional[str] = Field(default=None)
    treatment: str = Field(default="en eller flera behandlingar", min_length=1, max_length=128)
    location: str = Field(default="en av vara kliniker", min_length=1, max_length=128)
    order_number: Optional[str] = Field(
        default=None,
        description="Order number, vary per provider"
    )


class SendContext(TemplateFormat):
    subject_line: str = Field(
        default="Du har redan beställt friskvårdsbehandling hos oss. Boka nu!",
        min_length=1,
        max_length=64,
    )
    to_email: EmailStr


class EmailSendResponse(CustomBaseModel):
    id: str
    http_headers: Optional[Dict[str, str]] = None
