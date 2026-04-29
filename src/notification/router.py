from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse

from src.auth.dependencies import require_role
from src.auth.models import User
from src.notification.dependencies import craft_template_format
from src.notification.designer import EmailDesigner
from src.notification.schemas import SendContext, EmailSendResponse, TemplateFormat
from src.notification.service import EmailService


router = APIRouter(
    prefix="/api/v1/notification",
    tags=["api-notification"],
)


@router.post(
    "/",
    response_model=EmailSendResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a notification email",
    responses={
        200: {"description": "Notification email sent successfully"},
        401: {"description": "Authentication credentials were not provided or are invalid"},
        403: {"description": "Authenticated user does not have permission to send notification emails"},
        422: {"description": "Request payload is invalid or email content could not be built"},
    },
)
async def send_notify_email(
    _valid_user: Annotated[User, Depends(require_role("merchant", "admin"))],
    send_context: SendContext,
):
    return await EmailService.send_email(send_context)


@router.get(
    "/templates",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    summary="Render a notification email template preview",
    description="A public route to preview the email template structure with sample data.",
    responses={
        200: {"description": "HTML template rendered successfully"},
        422: {"description": "Request data is invalid for building the template preview"},
    },
)
async def preview_email_template(
    request: Request,
    order_info: Annotated[TemplateFormat, Depends(craft_template_format)],
):
    return EmailDesigner.render_template_preview(request, order_info)
