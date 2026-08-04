import asyncio
from db.session import async_session
from models.vehicle import Vehicle
from sqlalchemy import select, func

async def count():
    async with async_session() as session:
        result = await session.execute(select(func.count(Vehicle.id)).where(func.upper(Vehicle.brand) == 'FIAT'))
        print('Total FIAT:', result.scalar())
        result_neuf = await session.execute(select(func.count(Vehicle.id)).where(func.upper(Vehicle.brand) == 'FIAT', Vehicle.condition == 'Neuf'))
        print('Total FIAT Neuf:', result_neuf.scalar())

asyncio.run(count())
