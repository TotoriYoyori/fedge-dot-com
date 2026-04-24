from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate, make_msgid
import smtplib

import asyncer
import resend

from src.notification.exceptions import ResendEmailDeliveryError
from src.notification.designer import EmailDesigner
from src.notification.schemas import SendContext, SendResponse
from src.notification.settings import notification_settings as ns


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
        await asyncer.asyncify(EmailService._resend_send)(send_context)
        return SendResponse()

    @staticmethod
    def _resend_send(send_context: SendContext) -> None:
        """Send an email using the Resend API."""
        resend.api_key = ns.RESEND_API_KEY

        html_body = EmailDesigner.write_email_html(send_context)
        plain_body = EmailDesigner.write_email_plaintext(send_context)

        try:
            params: dict = {
                "from": f"{ns.smtp_from_name} <{ns.smtp_username}>",
                "to": [send_context.to_email],
                "subject": send_context.subject_line,
                "html": html_body,
                "text": plain_body,
                "headers": {
                    "Message-ID": make_msgid(),
                    "Date": formatdate(localtime=True),
                },
            }
            resend.Emails.send(resend.Emails.SendParams(params))
        except Exception:
            raise ResendEmailDeliveryError

    @staticmethod
    def _smtp_send(send_context: SendContext) -> None:
        """
        Synchronous internal implementation for sending email.
        """
        html_body = EmailDesigner.write_email_html(send_context)
        plain_body = EmailDesigner.write_email_plaintext(send_context)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = Header(send_context.subject_line, "utf-8")
        msg["From"] = formataddr(
            (
                str(Header(ns.smtp_from_name, "utf-8")),
                ns.smtp_username,
            )
        )
        msg["To"] = send_context.to_email
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid()

        msg.attach(MIMEText(plain_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(ns.smtp_host, ns.smtp_port) as server:
            server.starttls()
            server.login(ns.smtp_username, ns.smtp_password)
            server.send_message(msg)
