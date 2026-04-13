from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base, AsyncSessionLocal
from .google.service import ensure_google_oauth_schema

from .dummies.router import router as dummies_router
from .google.router import router as google_router
from .auth.router import router as auth_router
from .notification.router import router as notification_router


# --------------- STARTUP AND SHUTDOWN LOGICS
@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await ensure_google_oauth_schema(session)

    yield


# --------------- APP INITIALIZATION
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url="/openapi.json" if settings.ENVIRONMENT in ('local', 'staging') else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dummies_router)
app.include_router(google_router)
app.include_router(auth_router)
app.include_router(notification_router)
