import asyncio

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User


async def seed_admin_user() -> None:
    from app.db import init_db

    await init_db()
    existing = await User.find_one(User.email == settings.seed_admin_email)
    if existing:
        print(f"Admin user already exists for {settings.seed_admin_email}")
        return

    user = User(
        username="admin",
        email=settings.seed_admin_email,
        hashed_password=hash_password(settings.seed_admin_password),
    )
    await user.insert()
    print(f"Created admin user: {settings.seed_admin_email}")


if __name__ == "__main__":
    asyncio.run(seed_admin_user())
