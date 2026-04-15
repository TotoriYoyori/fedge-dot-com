from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dummies.exceptions import DummyNotFound, DummyWithNameExists
from src.dummies.models import Dummy
from src.dummies.service import DummyService


async def valid_dummy_id(dummy_id: int, db: AsyncSession = Depends(get_db)) -> Dummy:
    dummy = await DummyService.get_by_id(db, dummy_id)
    if not dummy:
        raise DummyNotFound

    return dummy


# --------------- EXISTENCE BOOL CHECKER (*_exists)
async def dummy_with_name_exists(
    dummy_create: "DummyCreate", db: Annotated[AsyncSession, Depends(get_db)]
) -> bool:
    """
    Checks if a dummy with the same name already exists in the database.
    """
    from src.dummies.service import DummyService

    dummy = await DummyService.get_by_name(dummy_create.name, db)
    if dummy:
        raise DummyWithNameExists

    return False
