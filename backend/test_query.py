import asyncio
from sqlalchemy import select, func, or_
from app.core.database import async_session_factory
from app.models.vehicle import Vehicle

async def main():
    async with async_session_factory() as db:
        query = select(Vehicle)
        brand = "Dacia"
        if brand:
            query = query.where(Vehicle.brand.ilike(f"%{brand}%"))
        
        condition = 'occasion'
        if condition == 'neuf':
            query = query.where(Vehicle.description.ilike('%Véhicule Neuf Officiel%'))
        elif condition == 'occasion':
            query = query.where(
                or_(
                    Vehicle.description == None,
                    ~Vehicle.description.ilike('%Véhicule Neuf Officiel%')
                )
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        print("Total occasion:", total)

        # test neuf
        query2 = select(Vehicle).where(Vehicle.brand.ilike(f"%{brand}%"))
        query2 = query2.where(Vehicle.description.ilike('%Véhicule Neuf Officiel%'))
        count_query2 = select(func.count()).select_from(query2.subquery())
        total_result2 = await db.execute(count_query2)
        total2 = total_result2.scalar() or 0
        print("Total neuf:", total2)

if __name__ == "__main__":
    asyncio.run(main())
