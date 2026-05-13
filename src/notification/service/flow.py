from src.notification.schemas import (
    EmailProviderPayload,
    EmailSendPayload,
    EmailSendResponse,
)
from src.notification.service.client import email_provider, send_with_provider
from src.notification.service.email import write_email_html, write_email_plaintext


async def send_email(send_payload: EmailSendPayload) -> EmailSendResponse:
    html_body = write_email_html(send_payload)
    plain_body = write_email_plaintext(send_payload)
    provider_payload = EmailProviderPayload(
        to_email=send_payload.to_email,
        subject_line=send_payload.subject_line,
        html_body=html_body,
        plain_body=plain_body,
    )

    return await send_with_provider(email_provider, provider_payload)
