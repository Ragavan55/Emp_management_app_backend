from __future__ import annotations

import re
from datetime import date, datetime
from typing import Literal

from beanie import Document
from pydantic import EmailStr, Field, field_validator


class Employee(Document):
    name: str = Field(..., min_length=1)
    email: EmailStr
    phone: str
    department: str = Field(..., min_length=1)
    designation: str = Field(..., min_length=1)
    joining_date: date
    status: Literal["Active", "Inactive"] = "Active"
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name cannot be empty")
        return value.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Phone number is required")
        if not re.fullmatch(r"\+?[0-9]{10,15}", cleaned):
            raise ValueError("Phone must be a valid 10-digit or E.164 format number")
        return cleaned

    @field_validator("joining_date")
    @classmethod
    def validate_joining_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Joining date cannot be in the future")
        return value

    class Settings:
        name = "employees"
        indexes = [
            [("email", 1), ("unique", True)],
            [("department", 1), ("status", 1)],
        ]

    class Config:
        json_schema_extra = {"example": {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "9876543210",
            "department": "Engineering",
            "designation": "Senior Developer",
            "joining_date": "2024-01-15",
            "status": "Active",
        }}
