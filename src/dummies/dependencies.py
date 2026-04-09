from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from .models import Dummy
from .service import DummyService
from .exceptions import DummyNotFound


async def valid_dummy_id(dummy_id: int, db: AsyncSession = Depends(get_db)) -> Dummy:
    dummy = await DummyService.get_by_id(db, dummy_id)
    if not dummy:
        raise DummyNotFound

    return dummy
