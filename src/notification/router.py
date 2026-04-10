from typing import Annotated
from pathlib import Path

from fastapi import APIRouter, Request, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..auth.models import User
from ..auth.dependencies import valid_access_token
from .designer import EmailDesigner
from .service import EmailService
from .schemas import SendContext, SendResponse
from .dependencies import craft_template_format

router = APIRouter(prefix="/notification", tags=["notification"])
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

@router.post(
    "/",
    response_model=SendResponse,
    status_code=status.HTTP_200_OK
)
async def send_notify_email(
    valid_user: Annotated[User, Depends(valid_access_token)],
    send_context: SendContext,
    html_body: Annotated[str, Depends(EmailDesigner.write_email_html)],
):
    if not valid_user:
        return None

    return EmailService.send_email(send_context, html_body)


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
        name=f"ho_1.html",
        context=order_info,
    )
