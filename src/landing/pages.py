from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from fastapi.requests import Request

from src.auth.dependencies import valid_cookie_token
from src.auth.models import User
from src.landing.redirect import LandingRedirect
from src.schemas import RouteDecoratorPreset
from src.templates import templates

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
        name=LandingRedirect.HOME_PAGE,
        context={"current_user": current_user},
    )
