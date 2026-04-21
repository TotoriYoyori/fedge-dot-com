from fastapi import APIRouter, status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from src.landing.settings import landing_settings, landing_page

page = APIRouter(tags=['ssr'])


@page.get(
    '/home',
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    summary="Render the home landing page",
    responses={
        200: {"description": "HTML template rendered successfully"},
        404: {"description": "HTML template rendered failed"},
    },
)
async def home(request: Request):
    return landing_page.TemplateResponse(
        request=request,
        name=landing_settings.HOME_PAGE,
        context={},
    )
