from src.notification.schemas import SendContext
from src.notification.service.email import write_email_html, write_email_plaintext


class EmailDesigner:
    @staticmethod
    def write_email_html(context: SendContext) -> str:
        return write_email_html(context)

    @staticmethod
    def write_email_plaintext(context: SendContext) -> str:
        return write_email_plaintext(context)
