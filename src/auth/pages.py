from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import (
    valid_login_credentials,
    valid_cookie_token,
)
from src.auth.models import User
from src.auth.schemas import AuthCreate
from src.auth.security import AuthSecurity
from src.auth.service import AuthService
from src.auth.responses import AuthResponse
from src.auth.settings import AuthNav
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
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name=AuthNav.REGISTER_PAGE,
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
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    form = await request.form()
    form_data = dict(form)

    try:
        auth_create = AuthCreate.model_validate(form_data)
    except ValidationError:
        return templates.TemplateResponse(
            request=request,
            name=AuthNav.REGISTER_PAGE,
            context={"error": "Please provide a valid username, email, and password."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    existing_user = await AuthService.get_one_by("username", auth_create.username, db)
    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name=AuthNav.REGISTER_PAGE,
            context={"error": "Username already taken, please choose another one."},
            status_code=status.HTTP_409_CONFLICT,
        )

    created_user = await AuthService.create(auth_create, db)
    token = AuthSecurity.create_access_token(
        data={"sub": str(created_user.id), "role": str(created_user.role)},
    )

    return AuthResponse.store_cookie_response(token)


@page.get("/login", name="login_page", response_class=HTMLResponse, response_model=None)
async def login_page(
    request: Request,
    current_user: Annotated[User | None, Depends(valid_cookie_token)],
):
    if current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name=AuthNav.LOGIN_PAGE,
        context={},
    )


@page.post("/login", name="login_submit", response_class=HTMLResponse, response_model=None)
async def login_submit(
    request: Request,
    valid_user: Annotated[User, Depends(valid_login_credentials)],
):
    if not valid_user:
        return templates.TemplateResponse(
            request=request,
            name=AuthNav.LOGIN_PAGE,
            context={"error": "Invalid username or password."},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    token = AuthSecurity.create_access_token(
        data={"sub": str(valid_user.id), "role": str(valid_user.role)},
    )
    return AuthResponse.store_cookie_response(token)



@page.get("/dashboard", name="dashboard_page", response_class=HTMLResponse, response_model=None)
async def dashboard(
    request: Request,
    current_user: Annotated[Optional[User], Depends(valid_cookie_token)],
):
    if not current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name=AuthNav.DASHBOARD_PAGE,
        context={"user": current_user},
    )


@page.post("/logout", name="logout_page", response_model=None)
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")

    return response
