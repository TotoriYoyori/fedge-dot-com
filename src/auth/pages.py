from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from src.auth.models import User
from src.auth.security import AuthSecurity
from src.auth.settings import auth_settings, auth_page
from src.auth.dependencies import valid_login_credentials, valid_cookie_token

page = APIRouter(tags=["ssr"])

@page.get("/register", response_class=HTMLResponse, response_model=None)
async def register_page(
    request: Request,
    current_user: Annotated[User | None, Depends(valid_cookie_token)],
):
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    return auth_page.TemplateResponse(
        request=request,
        name=auth_settings.REGISTER_PAGE,
        context={},
    )


@page.get("/login", response_class=HTMLResponse, response_model=None)
async def login_page(
    request: Request,
    current_user: Annotated[User | None, Depends(valid_cookie_token)],
):
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    return auth_page.TemplateResponse(
        request=request,
        name=auth_settings.LOGIN_PAGE,
        context={},
    )


@page.post("/login", response_class=HTMLResponse, response_model=None)
async def login_submit(
    request: Request,
    valid_user: Annotated[User, Depends(valid_login_credentials)],
):
    if not valid_user:
        return auth_page.TemplateResponse(
            request=request,
            name=auth_settings.LOGIN_PAGE,
            context={"error": "Invalid username or password."},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    access_token_expires = timedelta(minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = AuthSecurity.create_access_token(
        data={"sub": str(valid_user.id), "role": str(valid_user.role)},
        expires_delta=access_token_expires,
    )

    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,        # JS cannot access this
        secure=True,          # HTTPS only in production
        samesite="lax",       # CSRF protection
        max_age=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


@page.get("/dashboard", response_class=HTMLResponse, response_model=None)
async def dashboard(
    request: Request,
    current_user: Annotated[User, Depends(valid_cookie_token)],
):
    return auth_page.TemplateResponse(
    request=request,
    name="dashboard.html",
    context={"user": current_user},
)


@page.post("/logout", response_model=None)
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


# @router.post("/register", response_class=HTMLResponse)
# async def register_submit(
#     request: Request,
#     db: Annotated[AsyncSession, Depends(get_db)],
# ):
#     form = await request.form()
#     auth_create = AuthCreate(
#         username=form["username"],
#         email=form["email"],
#         password=form["password"],
#     )
#
#     # reuse same service as your API route
#     try:
#         user = await AuthService.create(auth_create, db)
#         return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
#     except Exception as e:
#         return templates.TemplateResponse("auth/register.html", {
#             "request": request,
#             "error": str(e),
#         })