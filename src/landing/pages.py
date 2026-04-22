from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from fastapi.requests import Request

from src.auth.dependencies import valid_cookie_token
from src.auth.models import User
from src.landing.settings import landing_settings
from src.templates import templates
from src.schemas import RouteDecoratorPreset

# ---------------
page = APIRouter(tags=["ssr"])
# ---------------


@page.get(
    "/",
    name="home_page",
    summary="Render the home page",
    **RouteDecoratorPreset.html_get(),
)
async def home(
    request: Request,
    current_user: Annotated[Optional[User], Depends(valid_cookie_token)],
):
    return templates.TemplateResponse(
        request=request,
        name=landing_settings.HOME_PAGE,
        context={"current_user": current_user},
    )
