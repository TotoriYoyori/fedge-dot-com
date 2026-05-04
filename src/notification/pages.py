from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError

from src.auth.dependencies import require_role
from src.auth.models import User
from src.auth.redirect import valid_cookie_token
from src.notification.schemas import SendContext
from src.notification.service import EmailService
from src.schemas import RouteDecoratorPreset
from src.templates import Redirect, templates

# --------------- SSR PAGE ROUTER
page = APIRouter(prefix="/notification", tags=["ssr"])


@page.get(
    "/",
    name="send_notification_page",
    summary="Renders the page to send a promotional email",
    **RouteDecoratorPreset.html_get(),
)
async def send_notification_page(
    request: Request,
    current_user: Annotated[Optional[User], Depends(valid_cookie_token)],
):
    if not current_user:
        return Redirect.to_home()

    # Check for merchant/admin role for SSR as well
    if current_user.role not in ("merchant", "admin"):
        return Redirect.to_home()

    return templates.TemplateResponse(
        request=request,
        name="send_notification.html",
        context={"user": current_user, "current_user": current_user},
    )


@page.post(
    "/",
    name="send_notification_submit",
    summary="Submit the form to send a promotional email",
    **RouteDecoratorPreset.html_post(),
)
async def send_notification_submit(
    request: Request,
    current_user: Annotated[User, Depends(require_role("merchant", "admin", use_cookie=True))],
):
    form = await request.form()
    form_data = dict(form)
    
    try:
        send_context = SendContext.model_validate(form_data)
    except ValidationError:
        # For simplicity, we can render the same page with an error or let global handler catch it
        # Here we follow the auth pattern of raising an exception if needed, 
        # but let's try to render back with error if we had a specific one.
        # Since I don't want to overcomplicate, I'll just re-raise or handle.
        return templates.TemplateResponse(
            request=request,
            name="send_notification.html",
            context={
                "user": current_user, 
                "current_user": current_user,
                "error": "Invalid form data. Please check your inputs."
            },
            status_code=400
        )

    response = await EmailService.send_email(send_context)

    return templates.TemplateResponse(
        request=request,
        name="send_notification.html",
        context={
            "user": current_user,
            "current_user": current_user,
            "success": True,
            "email_id": response.id
        },
    )
