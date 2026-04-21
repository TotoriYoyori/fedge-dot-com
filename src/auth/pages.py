from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.database import get_db
from src.auth.schemas import AuthCreate
from src.auth.service import AuthService
from src.auth.settings import auth_settings, auth_renderer
from src.auth.dependencies import username_already_exists, authenticated_exists

page = APIRouter(tags=["ssr"])

@page.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return auth_renderer.TemplateResponse(
        request=request,
        name=auth_settings.DEFAULT_TEMPLATE_NAME,
        context={},
    )

#
# @page.get("/login", response_class=HTMLResponse)
# async def login_page(request: Request):
#     return auth_renderer.TemplateResponse(
#         request=request,
#         name="login.html",
#         context={},
#     )


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