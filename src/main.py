from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware

from src.config import settings
from src.database import engine, Base
from src.dummies.router import router as dummies_router

SHOW_DOCS = settings.ENVIRONMENT in ('local', 'staging')

@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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
