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
from src.auth.redirect import AuthRedirect
from src.auth.schemas import AuthCreate
from src.auth.security import AuthSecurity
from src.auth.service import AuthService
from src.database import get_db
from src.schemas import RouteDecoratorPreset
from src.templates import templates

# --------------- PAGE ROUTING
page = APIRouter(tags=["ssr"])

@page.get(
    "/register",
    name="register_page",
    summary="Renders the page where user can register a new account",
    **RouteDecoratorPreset.html_get()
)
async def register_page(
    request: Request,
    current_user: Annotated[User | None, Depends(valid_cookie_token)],
):
    if current_user:
        return AuthRedirect.to_home()

    return templates.TemplateResponse(
        request=request,
        name=AuthRedirect.REGISTER_PAGE,
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
    current_user: Annotated[User | None, Depends(valid_cookie_token)],
):
    if current_user:
        return AuthRedirect.to_home()

    form = await request.form()
    form_data = dict(form)
    try:
        auth_create = AuthCreate.model_validate(form_data)
    except ValidationError:
        raise InvalidFormData

    existing_user = await AuthService.get_one_by("username", auth_create.username, db)
    if existing_user:
        raise UsernameAlreadyExists

    created_user = await AuthService.create(auth_create, db)
    token = AuthSecurity.create_access_token(
        data={"sub": str(created_user.id), "role": str(created_user.role)},
    )

    return AuthRedirect.store_cookie(token)


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
        return AuthRedirect.to_home()

    return templates.TemplateResponse(
        request=request,
        name=AuthRedirect.LOGIN_PAGE,
        context={},
    )


@page.post(
    "/login",
    name="login_submit",
    summary="Send post to authenticate an existing user",
    **RouteDecoratorPreset.html_post(),
)
async def login_submit(
    request: Request,
    current_user: Annotated[User | None, Depends(valid_cookie_token)],
    valid_user: Annotated[User, Depends(valid_login_credentials)],
):
    # if current_user:
    #     return AuthRedirect.to_home()

    token = AuthSecurity.create_access_token(
        data={"sub": str(valid_user.id), "role": str(valid_user.role)},
    )
    return AuthRedirect.store_cookie(token)


@page.get(
    "/dashboard",
    name="dashboard_page",
    summary="Renders the dashboard page for the authenticated user",
    **RouteDecoratorPreset.html_get(),
)
async def dashboard(
    request: Request,
    current_user: Annotated[Optional[User], Depends(valid_cookie_token)],
):
    if not current_user:
        return AuthRedirect.to_home()

    return templates.TemplateResponse(
        request=request,
        name=AuthRedirect.DASHBOARD_PAGE,
        context={"user": current_user},
    )


@page.post(
    "/logout",
    name="logout_page",
    summary="Send post to log out the current user",
    **RouteDecoratorPreset.html_post(),
)
async def logout():
    return AuthRedirect.logout()
