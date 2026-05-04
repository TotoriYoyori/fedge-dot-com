from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import (
    valid_login_credentials,
)
from src.auth.models import User
from src.auth.redirect import (
    redirect_with_cookie,
    redirect_remove_cookie,
    no_duplicate_user_record,
    redirect_authenticated_user,
)
from src.auth.schemas import AuthCreate
from src.auth.service import create_user
from src.database import get_db
from src.schemas import RouteDecoratorPreset
from src.templates import Redirect, templates

# =============== SSR PAGE ROUTER ===============
page = APIRouter(tags=["ssr"])


@page.get(
    "/register",
    name="register_page",
    summary="Renders the page where user can register a new account",
    **RouteDecoratorPreset.html_get(),
)
async def register_page(
    request: Request,
    _to_home_if_authenticated: Annotated[None, Depends(redirect_authenticated_user)],
):
    return templates.TemplateResponse(
        request=request,
        name=Redirect.AUTH_REGISTER,
        context={},
    )


@page.post(
    "/register",
    name="register_submit",
    summary="Send post to register a new user",
    **RouteDecoratorPreset.html_post(),
)
async def register_submit(
    db: Annotated[AsyncSession, Depends(get_db)],
    _to_home_if_authenticated: Annotated[None, Depends(redirect_authenticated_user)],
    valid_create_schema: Annotated[AuthCreate, Depends(no_duplicate_user_record)],
):
    new_user = await create_user(valid_create_schema, db)

    return redirect_with_cookie(
        new_user,
        redirect_url=f"/users/{new_user.id}/dashboard"
    )


@page.get(
    "/login",
    name="login_page",
    summary="Renders the page where user can log into an account",
    **RouteDecoratorPreset.html_get(),
)
async def login_page(
    request: Request,
    _to_home_if_authenticated: Annotated[None, Depends(redirect_authenticated_user)],
):
    return templates.TemplateResponse(
        request=request,
        name=Redirect.AUTH_LOGIN,
        context={},
    )


@page.post(
    "/login",
    name="login_submit",
    summary="Send post to authenticate an existing user",
    **RouteDecoratorPreset.html_post(),
)
async def login_submit(
    _to_home_if_authenticated: Annotated[None, Depends(redirect_authenticated_user)],
    valid_login_user: Annotated[User, Depends(valid_login_credentials)],
):
    return redirect_with_cookie(
        valid_login_user,
        redirect_url=f"/users/{valid_login_user.id}/dashboard"
    )


@page.post(
    "/logout",
    name="logout_page",
    summary="Send post to log out the current user",
    **RouteDecoratorPreset.html_post(),
)
async def logout():
    return redirect_remove_cookie()
