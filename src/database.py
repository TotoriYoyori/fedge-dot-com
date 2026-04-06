from typing import AsyncGenerator
# ----- Dependencies Import
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
# ----- App Modules
from src.config import settings

# ---------------- ALEMBIC MIGRATION NAMING CONVENTION
NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "pk": "%(table_name)s_pkey",
}

# ---------------- MODEL BASE
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# ---------------- DB FACTORY
engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
