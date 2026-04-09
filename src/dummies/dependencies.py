from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from .models import Dummy
from .service import DummyService
from .exceptions import DummyNotFound, DummyNameAlreadyExists
from .schemas import DummyCreate


async def valid_dummy_id(dummy_id: int, db: AsyncSession = Depends(get_db)) -> Dummy:
    dummy = await DummyService.get_by_id(db, dummy_id)
    if not dummy:
        raise DummyNotFound

    return dummy


async def dummy_with_name_exists(
    dummy_create: DummyCreate,
    db: AsyncSession = Depends(get_db)
) -> bool:
    dummy = await DummyService.get_by_name(db, dummy_create.name)
    if dummy:
       raise DummyNameAlreadyExists

    return False
