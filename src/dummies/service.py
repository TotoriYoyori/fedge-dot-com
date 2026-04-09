# ----- Dependencies Import
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

# ----- Local Module
from .models import Dummy
from .schemas import DummyCreate, DummyUpdate, DummyPatch


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
    async def get_by_name(db: AsyncSession, dummy_name: str) -> Dummy | None:
        stmt = select(Dummy).where(
            func.lower(Dummy.name) == dummy_name.lower()
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(data: DummyCreate, db: AsyncSession) -> Dummy:
        dummy = Dummy(**data.model_dump(exclude_none=True))
        db.add(dummy)
        await db.commit()
        await db.refresh(dummy)

        return dummy

    @staticmethod
    async def update(dummy_update: DummyUpdate, dummy: Dummy, db: AsyncSession) -> Dummy:
        new_data = dummy_update.model_dump()
        for field, new_value in new_data.items():
            setattr(dummy, field, new_value)

        await db.commit()
        await db.refresh(dummy)

        return dummy

    @staticmethod
    async def patch(dummy_patch: DummyPatch, dummy: Dummy, db: AsyncSession) -> Dummy:
        new_data = dummy_patch.model_dump(exclude_unset=True, exclude_none=True)
        for field, new_value in new_data.items():
            setattr(dummy, field, new_value)

        await db.commit()
        await db.refresh(dummy)

        return dummy


    @staticmethod
    async def delete(dummy: Dummy, db: AsyncSession) -> Dummy:
        await db.delete(dummy)
        await db.commit()

        return dummy
