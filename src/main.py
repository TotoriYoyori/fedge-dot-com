from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.config import settings
from src.database import Base, engine

from src.auth import exceptions as auth_exceptions

from src.landing.pages import page as landing_page
from src.auth.pages import page as auth_page

from src.auth.router import router as auth_router
from src.notification.router import router as notification_router

# --------------- STARTUP AND SHUTDOWN LOGICS
@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

# --------------- APP INITIALIZATION
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url="/openapi.json" if settings.ENVIRONMENT in ("local", "staging") else None,
    lifespan=lifespan,
)


# --------------- REGISTER EXCEPTION HANDLERS
auth_exceptions.register_exception_handlers(app)

# --------------- REGISTER MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------- REGISTER STATIC FILES
app.mount("/static/landing", StaticFiles(directory="src/landing/static"), name="landing-static")
app.mount("/static/auth", StaticFiles(directory="src/auth/static"), name="auth-static")

# --------------- REGISTER ROUTER & SSR PAGES
app.include_router(landing_page)
app.include_router(auth_page)

app.include_router(auth_router)
app.include_router(notification_router)
