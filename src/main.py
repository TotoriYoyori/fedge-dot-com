from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.auth import exceptions as auth_exceptions
from src.auth.router import router as auth_router
from src.config import settings
from src.database import AsyncSessionLocal, Base, engine
from src.google.router import router as google_router
from src.google.service import ensure_google_oauth_schema
from src.notification.router import router as notification_router
from src.users.router import router as users_router

NOTIFICATION_STATIC_DIR = Path(__file__).resolve().parent / "notification" / "static"


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
    openapi_url=(
        "/openapi.json" if settings.ENVIRONMENT in ("local", "staging") else None
    ),
    lifespan=lifespan,
)


# --------------- GLOBAL EXCEPTION HANDLERS
@app.exception_handler(auth_exceptions.UsernameAlreadyExists)
async def username_already_exists_handler(request: Request, exc: auth_exceptions.UsernameAlreadyExists):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Username already exists. Please register with a different username."},
    )


@app.exception_handler(auth_exceptions.UnauthenticatedUser)
async def unauthenticated_user_handler(request: Request, exc: auth_exceptions.UnauthenticatedUser):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Unauthenticated. Incorrect username or password."},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(auth_exceptions.MalformedToken)
async def malformed_token_handler(request: Request, exc: auth_exceptions.MalformedToken):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Malformed token. Please log in and try again."},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(auth_exceptions.UserNotFound)
async def user_not_found_handler(request: Request, exc: auth_exceptions.UserNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "User not found."},
    )


@app.exception_handler(auth_exceptions.AlreadyAuthenticated)
async def already_authenticated_handler(request: Request, exc: auth_exceptions.AlreadyAuthenticated):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "Already authenticated. Logout to access this resource."},
    )


@app.exception_handler(auth_exceptions.InsufficientPermission)
async def insufficient_permission_handler(request: Request, exc: auth_exceptions.InsufficientPermission):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "Insufficient permissions"},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(google_router)
app.include_router(auth_router)
app.include_router(notification_router)
app.mount(
    "/notification/static",
    StaticFiles(directory=str(NOTIFICATION_STATIC_DIR)),
    name="static",
)
app.include_router(users_router)
