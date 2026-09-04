from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.models.employee import Employee
from app.models.user import User

from pymongo.errors import ServerSelectionTimeoutError
import sys


client = AsyncIOMotorClient(settings.mongodb_url)
database = client[settings.database_name]


async def init_db() -> None:
    global client, database
    try:
        await init_beanie(database=database, document_models=[Employee, User])
    except ServerSelectionTimeoutError as e:
        msg = (
            "MongoDB server selection timeout or TLS certificate verification failed. "
            "This commonly happens when the host machine clock is incorrect. "
            "On Windows run: `w32tm /resync` (Admin) and retry."
        )
        print(msg, file=sys.stderr)

        # Development fallback: retry with invalid TLS certificates allowed so
        # local clock or cert issues don't block development. NOT RECOMMENDED
        # FOR PRODUCTION — this disables certificate verification.
        try:
            print(
                "Retrying DB init with tlsAllowInvalidCertificates=True (INSECURE fallback)",
                file=sys.stderr,
            )
            fallback_client = AsyncIOMotorClient(
                settings.mongodb_url, tlsAllowInvalidCertificates=True
            )
            fallback_db = fallback_client[settings.database_name]
            await init_beanie(database=fallback_db, document_models=[Employee, User])
            # swap in fallback client/database for lifespan cleanup
            client.close()
            client = fallback_client
            database = fallback_db
            print(
                "Connected to MongoDB with INSECURE fallback (tlsAllowInvalidCertificates=True).",
                file=sys.stderr,
            )
            return
        except Exception as e2:
            print("Fallback DB init also failed:", e2, file=sys.stderr)
            raise RuntimeError(msg) from e
    except Exception as e:
        print("Failed to initialize database:", e, file=sys.stderr)
        raise


@asynccontextmanager
async def lifespan() -> AsyncIterator[None]:
    await init_db()
    try:
        yield
    finally:
        client.close()
