from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import (
    valid_cookie_token,
    valid_login_credentials,
)
from src.auth.exceptions import InvalidFormData, UsernameAlreadyExists
from src.auth.models import User
from src.auth.redirect import (
    create_cookie,
    logout as logout_redirect,
    redirect_authenticated_user,
)
from src.auth.schemas import AuthCreate
from src.auth.service import create_user, get_user_by
from src.database import get_db
from src.schemas import RouteDecoratorPreset
from src.templates import Redirect, templates

# --------------- SSR PAGE ROUTER
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
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    _to_home_if_authenticated: Annotated[None, Depends(redirect_authenticated_user)],
):
    form = await request.form()
    form_data = dict(form)
    try:
        auth_create = AuthCreate.model_validate(form_data)
    except ValidationError:
        raise InvalidFormData

    existing_user = await get_user_by("username", auth_create.username, db)
    if existing_user:
        raise UsernameAlreadyExists

    created_user = await create_user(auth_create, db)

    return create_cookie(created_user, redirect_url=f"/users/{created_user.id}/dashboard")


@page.get(
    "/login",
    name="login_page",
    summary="Renders the page where user can log into an account",
    **RouteDecoratorPreset.html_get(),
)
async def login_page(
    request: Request,
    current_user: Annotated[User | None, Depends(valid_cookie_token)],
):
    if current_user:
        return Redirect.to_home()

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
    _request: Request,
    current_user: Annotated[User | None, Depends(valid_cookie_token)],
    valid_user: Annotated[User, Depends(valid_login_credentials)],
):
    if current_user:
        return Redirect.to_home()

    return create_cookie(valid_user, redirect_url=f"/users/{valid_user.id}/dashboard")


@page.post(
    "/logout",
    name="logout_page",
    summary="Send post to log out the current user",
    **RouteDecoratorPreset.html_post(),
)
async def logout():
    return logout_redirect()
