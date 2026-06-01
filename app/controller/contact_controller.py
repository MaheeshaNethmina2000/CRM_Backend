from uuid import UUID
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from app.config.database_config import get_db
from app.service.contact_service import ContactService

# Import security to lock down the update/delete routes to Admins only
from app.enums.enums import UserRole
from app.util.security import require_roles

router = APIRouter(
    prefix="/v1/api/contacts",
    tags=["Contacts"],
)


class ContactCreateRequest(BaseModel):
    # staff_id is completely REMOVED from creation.
    # New contacts are unassigned by default.
    first_name: str
    last_name: str
    phone_number: str
    address: Optional[str] = None


class ContactUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    # Admins will use this field later to assign the contact to an agent
    staff_id: Optional[UUID] = None


# PUBLIC ROUTE: No security required. A student on your website can trigger this.
@router.post("/")
async def create_contact(
        response: Response,
        request: ContactCreateRequest,
        db: AsyncSession = Depends(get_db),
):
    contact_data = request.model_dump()

    # Explicitly set staff_id to None so it enters the database as "Unassigned"
    contact_data["staff_id"] = None

    result = await ContactService.create_contact(contact_data, db)
    response.status_code = result.status_code
    return result


# INTERNAL ROUTE: Anyone logged in can view a contact
@router.get("/{contact_id}")
async def get_contact(
        response: Response,
        contact_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(
            require_roles([UserRole.SYSTEM_ADMIN, UserRole.WHATSAPP_AGENT, UserRole.CALL_CENTER_AGENT]))
):
    result = await ContactService.get_contact_by_id(contact_id, db)
    response.status_code = result.status_code
    return result


# ADMIN ROUTE: Only System Admins can assign a staff member to a contact
@router.patch("/{contact_id}")
async def update_contact(
        response: Response,
        contact_id: UUID,
        request: ContactUpdateRequest,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    result = await ContactService.update_contact(contact_id, request.model_dump(exclude_unset=True), db)
    response.status_code = result.status_code
    return result


# ADMIN ROUTE: Only System Admins can delete
@router.delete("/{contact_id}")
async def delete_contact(
        response: Response,
        contact_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    result = await ContactService.delete_contact(contact_id, db)
    response.status_code = result.status_code
    return result


# INTERNAL ROUTE: Agents and Admins can view lists
@router.get("/")
async def get_all_contacts(
        response: Response,
        page: int = 1,
        limit: int = 10,
        staff_id: UUID = None,
        search: str = None,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(
            require_roles([UserRole.SYSTEM_ADMIN, UserRole.WHATSAPP_AGENT, UserRole.CALL_CENTER_AGENT]))
):
    result = await ContactService.get_all_contacts(db, page, limit, staff_id, search)
    response.status_code = result.status_code
    return result