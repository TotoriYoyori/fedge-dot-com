from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.auth.dependencies import valid_access_token
from src.auth.models import User
from src.notification.dependencies import craft_template_format
from src.notification.designer import EmailDesigner
from src.notification.schemas import SendContext, SendResponse
from src.notification.service import EmailService

router = APIRouter(prefix="/notification", tags=["notification"])
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@router.post("/", response_model=SendResponse, status_code=status.HTTP_200_OK)
async def send_notify_email(
    valid_user: Annotated[User, Depends(valid_access_token)],
    send_context: SendContext,
    html_body: Annotated[str, Depends(EmailDesigner.write_email_html)],
):
    if not valid_user:
        return None

    return await EmailService.send_email(send_context, html_body)


@router.get(
    "/templates",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def preview_email_template(
    request: Request,
    order_info: Annotated[dict, Depends(craft_template_format)],
):
    return templates.TemplateResponse(
        request=request,
        name="ho_2.html",
        context=order_info,
    )
