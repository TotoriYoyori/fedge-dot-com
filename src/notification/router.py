from typing import Annotated
from pathlib import Path

from fastapi import APIRouter, Request, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

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
    send_context: SendContext,
    html_body: Annotated[str, Depends(EmailDesigner.write_email_html)],
):
    return await EmailService.send_email(send_context, html_body)


@router.get(
    "/templates",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
async def render_email_template(
    request: Request,
    order_info: Annotated[dict, Depends(craft_template_format)],
):
    return templates.TemplateResponse(
        request=request,
        name=f"ho_1.html",
        context=order_info,
    )
