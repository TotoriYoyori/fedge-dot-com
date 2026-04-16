import datetime as dt
from typing import Optional

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
        default="Din behandling vantar pa att bokas!",
        min_length=1,
        max_length=64,
    )
    to_email: EmailStr


class SendResponse(CustomBaseModel):
    sent_time: str = Field(
        default_factory=lambda: dt.datetime.now().strftime("%Y-%m-%d %H-%M-%S"),
    )
    message: str = "Email successfully sent!"
