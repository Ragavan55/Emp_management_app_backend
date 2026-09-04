import asyncio
import getpass
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


async def create_user():
    await init_db()
    email = input("Email: ").strip()
    if not email:
        print("Email is required")
        return
    username = input("Username (leave empty to use local-part of email): ").strip()
    if not username:
        username = email.split("@")[0]
    password = getpass.getpass("Password: ")
    if not password:
        print("Password is required")
        return

    # bcrypt has a 72-byte input limit; truncate UTF-8 bytes if necessary
    pw_bytes = password.encode("utf-8")
    if len(pw_bytes) > 72:
        print("Warning: password is longer than 72 bytes — it will be truncated to 72 bytes for bcrypt.")
        pw_bytes = pw_bytes[:72]
        password = pw_bytes.decode("utf-8", errors="ignore")

    existing = await User.find_one(User.email == email)
    if existing:
        print(f"User with email {email} already exists")
        return

    try:
        hashed = hash_password(password)
    except Exception as e:
        print("Failed to hash password — is bcrypt installed correctly?", e)
        print("Ensure `bcrypt` is installed in the virtualenv (pip install bcrypt) and try again.")
        return

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
    asyncio.run(create_user())
