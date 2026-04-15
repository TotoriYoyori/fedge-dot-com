import datetime as dt

from pydantic import BaseModel, EmailStr, Field


from src.schemas import CustomBaseModel


class SendContext(CustomBaseModel):
    subject_line: str = Field(..., min_length=1, max_length=64)
    to_email: EmailStr


class SendResponse(SendContext):
    sent_time: str = Field(
        default_factory=lambda: dt.datetime.now().strftime("%Y-%m-%d %H-%M-%S"),
    )
    message: str = "Email successfully sent!"


class TemplateFormat(CustomBaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    treatment: str = Field(..., min_length=1, max_length=64)
    location: str = Field(..., min_length=1, max_length=64)
    order_number: str = Field(
        ..., min_length=1, max_length=64, description="Order number, vary per provider"
    )
