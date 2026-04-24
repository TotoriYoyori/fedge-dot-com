from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from src.auth.exceptions import AuthExceptionHandler
from src.notification.exceptions import NotificationExceptionHandler
from src.auth.pages import page as auth_page
from src.auth.router import router as auth_router
from src.config import settings
from src.database import Base, engine
from src.landing.pages import page as landing_page
from src.notification.router import router as notification_router


# --------------- APPLICATION LIFECYCLE EVENTS
@asynccontextmanager
async def lifespan(_fastapi: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield


# --------------- FASTAPI INSTANCE CONFIGURATION
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=(
        "/openapi.json" if settings.ENVIRONMENT in ("local", "staging") else None
    ),
    lifespan=lifespan,
)


# --------------- DOMAIN ERROR HANDLERS
AuthExceptionHandler(app)
NotificationExceptionHandler(app)


# --------------- GLOBAL REQUEST MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# --------------- ASSET MOUNTING POINTS
BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static/landing",
    StaticFiles(directory=BASE_DIR / "landing" / "static"),
    name="landing-static",
)
app.mount(
    "/static/auth",
    StaticFiles(directory=BASE_DIR / "auth" / "static"),
    name="auth-static",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# --------------- API ROUTE REGISTRATION
app.include_router(landing_page)
app.include_router(auth_page)

app.include_router(auth_router)
app.include_router(notification_router)
