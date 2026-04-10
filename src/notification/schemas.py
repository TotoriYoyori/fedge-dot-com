import datetime as dt
from pydantic import BaseModel, Field, EmailStr


class SendContext(BaseModel):
    subject_line: str = Field(..., min_length=1, max_length=64)
    to_email: EmailStr


class SendResponse(SendContext):
    sent_time: str = Field(
        default_factory=lambda: dt.datetime.now().strftime("%Y-%m-%d %H-%M-%S"),
    )
    message: str = "Email successfully sent!"


class TemplateFormat(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    treatment: str = Field(..., min_length=1, max_length=64)
    location: str = Field(..., min_length=1, max_length=64)
    order_number: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Order number, vary per provider"
    )
