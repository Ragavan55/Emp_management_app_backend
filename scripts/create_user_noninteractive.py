import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Ensure `backend` is on sys.path when running this script directly
backend_dir = str(Path(__file__).resolve().parents[1])
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.security import hash_password
from app.db import init_db
from app.models.user import User


async def create_user(email: str, password: str, username: str | None = None):
    await init_db()
    if not username:
        username = email.split("@")[0]

    existing = await User.find_one(User.email == email)
    if existing:
        print(f"User with email {email} already exists")
        return

    hashed = hash_password(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await user.insert()
    print(f"Created user {email} (username: {username})")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: create_user_noninteractive.py <email> <password> [username]")
        sys.exit(1)
    email = sys.argv[1]
    password = sys.argv[2]
    username = sys.argv[3] if len(sys.argv) > 3 else None
    asyncio.run(create_user(email, password, username))
