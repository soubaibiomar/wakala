import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.core.database import Base
from app.models.chat_history import ChatSession, ChatMessage

async def create_tables():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created")

if __name__ == "__main__":
    asyncio.run(create_tables())
