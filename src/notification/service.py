from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

import asyncer

from src.config import settings
from src.notification.designer import EmailDesigner
from src.notification.schemas import SendContext, SendResponse


class EmailService:
    """Service for composing and sending notification emails.

    Wraps the SMTP delivery flow behind async-friendly class methods.
    """

    @staticmethod
    async def send_email(
        send_context: SendContext,
    ) -> SendResponse:
        """
        Send a single HTML email using smtplib.

        :param send_context: Delivery metadata and template context for the email.
        """
        await asyncer.asyncify(EmailService._send_sync)(send_context)
        return SendResponse()

    @staticmethod
    def _send_sync(send_context: SendContext) -> None:
        """
        Synchronous internal implementation for sending email.
        """
        html_body = EmailDesigner.write_email_html(send_context)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = send_context.subject_line
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USERNAME}>"
        msg["To"] = send_context.to_email

        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
