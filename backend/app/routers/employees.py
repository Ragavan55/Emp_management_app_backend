import math
import re
from datetime import datetime

from beanie import PydanticObjectId
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_current_user
from app.models.employee import Employee
from app.models.user import User
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate, PaginatedEmployeeResponse

router = APIRouter(prefix="/employees", tags=["employees"])


async def _get_employee_or_404(employee_id: str) -> Employee:
    if not ObjectId.is_valid(employee_id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid employee ID")
    employee = await Employee.get(PydanticObjectId(employee_id))
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


@router.get(
    "",
    response_model=PaginatedEmployeeResponse,
    summary="List employees",
    description="List employees with search, filtering, and pagination.",
)
async def list_employees(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = None,
    department: str | None = None,
    status: str | None = None,
    current_user: User = Depends(get_current_user),
) -> PaginatedEmployeeResponse:
    query: dict = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": re.escape(search), "$options": "i"}},
            {"email": {"$regex": re.escape(search), "$options": "i"}},
        ]
    if department:
        query["department"] = department
    if status:
        query["status"] = status

    total = await Employee.find(query).count()
    skip = (page - 1) * limit
    employees = await Employee.find(query).skip(skip).limit(limit).sort("-created_at").to_list()
    total_pages = max(1, math.ceil(total / limit)) if total else 1

    return PaginatedEmployeeResponse(
        items=[EmployeeRead.from_document(employee) for employee in employees],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@router.get(
    "/stats/summary",
    summary="Employee summary stats",
    description="Returns counts for total, active, and inactive employees.",
)
async def employee_summary(current_user: User = Depends(get_current_user)) -> dict[str, int]:
    total = await Employee.find().count()
    active = await Employee.find(Employee.status == "Active").count()
    inactive = await Employee.find(Employee.status == "Inactive").count()
    return {"total": total, "active": active, "inactive": inactive}


@router.get(
    "/{employee_id}",
    response_model=EmployeeRead,
    summary="Get employee by id",
    description="Fetch a single employee record.",
)
async def get_employee(employee_id: str, current_user: User = Depends(get_current_user)) -> EmployeeRead:
    employee = await _get_employee_or_404(employee_id)
    return EmployeeRead.from_document(employee)


@router.post(
    "",
    response_model=EmployeeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create employee",
    description="Create a new employee record.",
)
async def create_employee(payload: EmployeeCreate, current_user: User = Depends(get_current_user)) -> EmployeeRead:
    employee = Employee(**payload.model_dump())
    employee.created_at = datetime.utcnow()
    employee.updated_at = datetime.utcnow()
    try:
        await employee.insert()
    except Exception:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Employee with this email already exists")
    return EmployeeRead.from_document(employee)


@router.put(
    "/{employee_id}",
    response_model=EmployeeRead,
    summary="Update employee",
    description="Update an employee record.",
)
async def update_employee(
    employee_id: str,
    payload: EmployeeUpdate,
    current_user: User = Depends(get_current_user),
) -> EmployeeRead:
    employee = await _get_employee_or_404(employee_id)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)
    employee.updated_at = datetime.utcnow()
    try:
        await employee.save()
    except Exception:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Employee with this email already exists")
    return EmployeeRead.from_document(employee)


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete employee",
    description="Delete an employee record.",
)
async def delete_employee(employee_id: str, current_user: User = Depends(get_current_user)) -> None:
    employee = await _get_employee_or_404(employee_id)
    await employee.delete()
    return None
