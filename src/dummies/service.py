# ----- Dependencies Import
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
# ----- Local Module
from .models import Dummy
from .schemas import DummyCreate


class DummyService:
    """
    The dummy service abstract interactions between the schemas and the database. Simply, you put db
    query functions here, which in turns return ORM models.
    """
    @staticmethod
    async def get_all(db: AsyncSession) -> list[Dummy]:
        stmt = select(Dummy)
        result = await db.execute(stmt)
        return result.scalars().all()


    @staticmethod
    async def get_by_id(db: AsyncSession, dummy_id: int) -> Dummy | None:
        stmt = select(Dummy).where(Dummy.id == dummy_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


    @staticmethod
    async def create(db: AsyncSession, data: DummyCreate) -> Dummy:
        dummy = Dummy(**data.model_dump())
        db.add(dummy)
        await db.commit()
        await db.refresh(dummy)

        return dummy
