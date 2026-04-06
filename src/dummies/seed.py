import asyncio

from src.database import AsyncSessionLocal
from src.dummies.models import Dummy

async def seed_data():
    async with AsyncSessionLocal() as session:
        dummy_data = [
            Dummy(
                name="Vicente Delgago",
                email="vicente.delgado@example.com",
                phone="907-707-986"
            )
        ]

        session.add_all(dummy_data)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed_data())
