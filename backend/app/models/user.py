from __future__ import annotations

from datetime import datetime

from beanie import Document
from pydantic import EmailStr, Field


class User(Document):
    username: str = Field(..., min_length=3)
    email: EmailStr
    hashed_password: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Settings:
        name = "users"
        indexes = [[("email", 1)], [("username", 1)]]
