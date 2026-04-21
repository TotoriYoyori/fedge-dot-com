from typing import Annotated

from fastapi import APIRouter, status, Depends
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse

from src.auth.dependencies import valid_cookie_token
from src.auth.models import User
from src.landing.settings import landing_settings, landing_page


page = APIRouter(tags=['ssr'])


@page.get(
    '/',
    response_model=None,
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    summary="Render the home landing page",
    responses={
        200: {"description": "HTML template rendered successfully"},
        404: {"description": "HTML template rendered failed"},
    },
)
async def home(
    request: Request,
    current_user: Annotated[User | None, Depends(valid_cookie_token)],
):
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    return landing_page.TemplateResponse(
        request=request,
        name=landing_settings.HOME_PAGE,
        context={},
    )
