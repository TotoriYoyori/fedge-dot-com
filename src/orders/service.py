# ----- Dependencies Import
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
# ----- Local Module
from .models import Order
from .schemas import OrderCreate

# ----- Interact with the DB to find orders
class OrderService:
    """
    The service layer abstract interactions between the schemas and the database. Simply, you put db
    query functions here, which in turns return ORM models.
    """
    @staticmethod
    async def get_all(db: AsyncSession) -> list[Order]:
        stmt = select(Order)
        result = await db.execute(stmt)
        return result.scalars().all()


    @staticmethod
    async def get_by_id(db: AsyncSession, order_id: int) -> Order | None:
        stmt = select(Order).where(Order.id == order_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


    @staticmethod
    async def create(db: AsyncSession, data: OrderCreate) -> Order:
        new_order = Order(**data.model_dump())
        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)

        return new_order
