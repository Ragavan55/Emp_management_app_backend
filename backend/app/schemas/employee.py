from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    phone: str
    department: str = Field(..., min_length=1)
    designation: str = Field(..., min_length=1)
    joining_date: date
    status: Literal["Active", "Inactive"] = "Active"

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
        if not (len(cleaned) >= 10 and cleaned.isdigit()):
            raise ValueError("Phone must be a valid 10-digit number")
        return cleaned

    @field_validator("joining_date")
    @classmethod
    def validate_joining_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Joining date cannot be in the future")
        return value


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    pass


class EmployeeRead(EmployeeBase):
    id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_document(cls, document: object) -> "EmployeeRead":
        return cls(
            id=str(document.id),
            name=document.name,
            email=document.email,
            phone=document.phone,
            department=document.department,
            designation=document.designation,
            joining_date=document.joining_date,
            status=document.status,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )


class PaginatedEmployeeResponse(BaseModel):
    items: list[EmployeeRead]
    total: int
    page: int
    limit: int
    total_pages: int
