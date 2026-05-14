from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from src.auth.dependencies import require_role
from src.auth.models import User

from src.notification.schemas import (
    EmailSendRequest,
    EmailSendResponse,
    TemplatePreviewQuery,
)
from src.notification.service import send_email
from src.ssr.templating import Redirect, templates

# =============== ROUTER ===============
router = APIRouter(prefix="/api/v1/notification", tags=["api-notification"])


@router.post(
    "/",
    response_model=EmailSendResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a notification email",
    responses={
        200: {"description": "Notification email sent successfully"},
        401: {"description": "Authentication new_credential were not provided or are invalid"},
        403: {"description": "Authenticated user does not have permission to send notification emails"},
        422: {"description": "Request new_credental is invalid or email content could not be built"},
    },
)
async def send_notify_email(
    _valid_user: Annotated[User, Depends(require_role("admin"))],
    send_request: EmailSendRequest,
):
    return await send_email(send_request)


@router.get(
    "/templates",
    name="preview_notification_template_api",
    summary="Render a notification email template preview",
)
async def preview_email_template(
    request: Request,
    preview_order: Annotated[TemplatePreviewQuery, Depends()],
):
    return templates.TemplateResponse(
        request=request,
        name=Redirect.NOTIFICATION_HO_3,
        context=preview_order.model_dump(),
    )
