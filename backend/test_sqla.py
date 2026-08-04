from sqlalchemy import select, func
from app.models.vehicle import Vehicle

query = select(Vehicle)
query = query.where(Vehicle.brand.ilike("%dacia%"))
count_query = select(func.count()).select_from(query.subquery())
print(count_query)
