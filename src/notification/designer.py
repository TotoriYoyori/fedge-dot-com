from fastapi import Request
from jinja2 import Template

from src.notification.schemas import SendContext, TemplateFormat
from src.notification.settings import (
    notification_settings,
    template_env,
    template_renderer,
)


class EmailDesigner:
    @staticmethod
    def write_email_html(context: SendContext) -> str:
        template: Template = template_env.get_template(
            notification_settings.DEFAULT_TEMPLATE_NAME
        )
        return template.render(
            name=context.name.strip().split()[0] if context.name else "",
            treatment=context.treatment,
            location=context.location,
            order_number=context.order_number,
        )

    @staticmethod
    def write_email_plaintext(context: SendContext) -> str:
        greeting_name = f" {context.name}" if context.name else ""
        order_number_line = (
            f"\nOrdernummer: {context.order_number}" if context.order_number else ""
        )

        return (
            f"Hej{greeting_name}!\n\n"
            "En liten paminnelse att boka din behandling.\n\n"
            f"Du har tidigare bestallt {context.treatment} hos oss pa Hanna & Ong "
            "med ditt friskvardsbidrag, men har annu inte bokat din tid.\n\n"
            f"Klicka och boka din tid via Bokadirekt pa {context.location}.\n\n"
            "Malmo: https://www.bokadirekt.se/places/"
            "hanna-ong-therapy-art-limhamn-malmo-55196\n"
            "Helsingborg: https://www.bokadirekt.se/places/"
            "hanna-ong-therapy-art-helsingborg-39960\n\n"
            "Med vanliga halsningar,\n\n"
            "Om du redan har bokat hos oss, ignorera garna detta meddelande."
            f"{order_number_line}\n\n"
            "(c) 2026 Hanna & Ong"
        )

    @staticmethod
    def render_template_preview(request: Request, preview: TemplateFormat) -> str:
        return template_renderer.TemplateResponse(
            request=request,
            name=notification_settings.DEFAULT_TEMPLATE_NAME,
            context=preview.model_dump(),
        )
