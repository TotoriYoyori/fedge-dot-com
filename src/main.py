from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware

from src.config import settings
from src.database import engine, Base

from src.dummies.router import router as dummies_router
from src.google.router import router as google_router
from src.auth.router import router as auth_router
from src.notification.router import router as notification_router

from src.database import AsyncSessionLocal
from src.google.service import ensure_google_oauth_schema

SHOW_DOCS = settings.ENVIRONMENT in ('local', 'staging')

@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await ensure_google_oauth_schema(session)

    yield

app = FastAPI(
    title='Fedge API',
    version=settings.APP_VERSION,
    openapi_url="/openapi.json" if SHOW_DOCS else None,
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