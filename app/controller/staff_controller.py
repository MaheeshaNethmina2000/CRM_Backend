from uuid import UUID
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.config.database_config import get_db
from app.service.staff_service import StaffService
from app.enums.enums import UserRole

# Import the security dependency for Role-Based Access Control
from app.util.security import require_roles

router = APIRouter(
    prefix="/v1/api/staff",
    tags=["Staff"],
)

class StaffRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    is_active: bool = True

class StaffUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class StaffLoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
async def login_staff(
    response: Response,
    request: StaffLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await StaffService.login(request.model_dump(), db)
    response.status_code = result.status_code
    return result


@router.post("/register")
async def register_staff(
    response: Response,
    request: StaffRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await StaffService.register_staff(request.model_dump(), db)
    response.status_code = result.status_code
    return result


@router.get("/{staff_id}")
async def get_staff(
    response: Response,
    staff_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles([UserRole.SYSTEM_ADMIN, UserRole.WHATSAPP_AGENT, UserRole.CALL_CENTER_AGENT]))
):
    result = await StaffService.get_staff_by_id(staff_id, db)
    response.status_code = result.status_code
    return result


# Only a SYSTEM_ADMIN can update staff profiles (e.g., upgrading user roles)
@router.patch("/{staff_id}")
async def update_staff(
    response: Response,
    staff_id: UUID,
    request: StaffUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    result = await StaffService.update_staff(staff_id, request.model_dump(exclude_unset=True), db)
    response.status_code = result.status_code
    return result


# Only a SYSTEM_ADMIN can permanently delete a staff member
@router.delete("/{staff_id}")
async def delete_staff(
    response: Response,
    staff_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    result = await StaffService.delete_staff(staff_id, db)
    response.status_code = result.status_code
    return result


@router.get("/")
async def get_all_staff(
    response: Response,
    page: int = 1,
    limit: int = 10,
    is_active: bool = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles([UserRole.SYSTEM_ADMIN, UserRole.WHATSAPP_AGENT, UserRole.CALL_CENTER_AGENT]))
):
    result = await StaffService.get_all_staff(db, page, limit, is_active)
    response.status_code = result.status_code
    return result