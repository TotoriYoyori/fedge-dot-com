import os
import smtplib
from typing import Dict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..config import settings
from .schemas import SendContext


SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USE_TLS = True

# Default sender (can be overridden when calling send_email)
DEFAULT_SENDER = os.getenv("SMTP_USERNAME", "your_email@gmail.com")
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your_email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_app_password_here")

class EmailService:

    @staticmethod
    def send_email(
        send_context: SendContext,
        html_body: str,
    ):
        """
        Send a single HTML email using smtplib.

        :param send_context: Containing subject line and to-address.
        :param html_body: HTML body of the email.
        """
        # Create multipart message (HTML + plain text)
        msg = MIMEMultipart("alternative")
        msg["Subject"] = send_context.subject_line
        msg["From"] = settings.SMTP_USERNAME
        msg["To"] = send_context.to_email

        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)

        return send_context