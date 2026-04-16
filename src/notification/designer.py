from fastapi import Request
from jinja2 import Template

from src.notification.schemas import SendContext
from src.notification.settings import (
    NotificationSettings,
    template_env,
    template_renderer,
)


class EmailDesigner:
    @staticmethod
    def write_email_html(context: SendContext) -> str:
        template: Template = template_env.get_template(
            NotificationSettings.DEFAULT_TEMPLATE_NAME
        )
        return template.render(
            **context.model_dump(exclude={"subject_line", "to_email"})
        )

    @staticmethod
    def write_email_plaintext(context: SendContext) -> str:
        return f"""
    Hi {context.name},

    This is a friendly reminder to book your {context.treatment}.

    We look forward to seeing you soon!
    """

    @staticmethod
    def render_template_preview(request: Request, context: SendContext) -> str:
        return template_renderer.TemplateResponse(
            request=request,
            name=NotificationSettings.DEFAULT_TEMPLATE_NAME,
            context=context.model_dump(exclude={"subject_line", "to_email"}),
        )
