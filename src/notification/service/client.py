from email.utils import formatdate, make_msgid
from typing import Any, Protocol

import asyncer
import resend
from requests import RequestException
from resend.exceptions import NoContentError, ResendError

from src.notification.exceptions import EmailDeliveryError
from src.notification.schemas import (
    EmailProviderName,
    EmailProviderPayload,
    EmailSendResponse,
)
from src.notification.settings import notification_settings as ns


# =============== Generic Email Provider ===============
class EmailProvider[ProviderParams](Protocol):
    def build(self, provider_payload: EmailProviderPayload) -> ProviderParams: ...

    async def send(self, params: ProviderParams) -> EmailSendResponse: ...


# =============== RESEND EMAIL PROVIDER ===============
class ResendEmailProvider:
    def __init__(self) -> None:
        resend.api_key = ns.RESEND_API_KEY

    def build(self, payload: EmailProviderPayload) -> resend.Emails.SendParams:
        params = {
            "from": ns.email_from,
            "to": [payload.to_email],
            "subject": payload.subject_line,
            "html": payload.html_body,
            "text": payload.plain_body,
            "headers": {"Message-ID": make_msgid(), "Date": formatdate(localtime=True)},
        }
        return resend.Emails.SendParams(params)

    async def send(self, params: resend.Emails.SendParams) -> EmailSendResponse:
        try:
            response = await asyncer.asyncify(resend.Emails.send)(params)
        except (ResendError, NoContentError) as exc:
            raise EmailDeliveryError from exc

        return EmailSendResponse.model_validate(
            {
                **response,
                "provider": EmailProviderName.RESEND,
            }
        )


# =============== MAILTRAP EMAIL PROVIDER ===============
class MailtrapEmailProvider:
    def __init__(self) -> None:
        import mailtrap as mt

        self._mailtrap = mt
        self._client = mt.MailtrapClient(
            token=str(ns.MAILTRAP_API_KEY),
            sandbox=True,
            inbox_id=str(ns.MAILTRAP_SANDBOX_INBOX_ID),
        )

    def build(self, payload: EmailProviderPayload) -> Any:
        return self._mailtrap.Mail(
            sender=self._mailtrap.Address(
                email=str(ns.EMAIL_FROM_ADDRESS),
                name=ns.EMAIL_FROM_NAME,
            ),
            to=[self._mailtrap.Address(email=payload.to_email)],
            subject=payload.subject_line,
            html=payload.html_body,
            text=payload.plain_body,
            category="Notification",
        )

    async def send(self, params: Any) -> EmailSendResponse:
        try:
            response = await asyncer.asyncify(self._client.send)(params)
        except (self._mailtrap.MailtrapError, RequestException) as exc:
            raise EmailDeliveryError from exc

        return EmailSendResponse(
            id=_extract_mailtrap_message_id(response),
            provider=EmailProviderName.MAILTRAP,
            message="Notification email accepted by Mailtrap sandbox.",
        )


def _extract_mailtrap_message_id(response: Any) -> str | None:
    if isinstance(response, dict):
        message_ids = response.get("message_ids") or []
        return str(message_ids[0]) if message_ids else None

    message_ids = getattr(response, "message_ids", None) or []
    return str(message_ids[0]) if message_ids else None


def get_email_provider() -> EmailProvider[Any]:
    if ns.EMAIL_PROVIDER == EmailProviderName.MAILTRAP:
        return MailtrapEmailProvider()

    return ResendEmailProvider()


email_provider = get_email_provider()


async def send_with_provider[ParamsT](
    provider: EmailProvider[ParamsT],
    provider_payload: EmailProviderPayload,
) -> EmailSendResponse:
    params = provider.build(provider_payload)
    return await provider.send(params)
