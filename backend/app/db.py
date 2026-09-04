from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.models.employee import Employee
from app.models.user import User

client = AsyncIOMotorClient(settings.mongodb_url)
database = client[settings.database_name]


async def init_db() -> None:
    await init_beanie(database=database, document_models=[Employee, User])


@asynccontextmanager
async def lifespan() -> AsyncIterator[None]:
    await init_db()
    try:
        yield
    finally:
        client.close()
