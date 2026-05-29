from uuid import UUID
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from app.config.database_config import get_db
from app.service.contact_service import ContactService

router = APIRouter(
    prefix="/v1/api/contacts",
    tags=["Contacts"],
)


class ContactCreateRequest(BaseModel):
    staff_id: UUID
    first_name: str
    last_name: str
    phone_number: str
    address: Optional[str] = None


class ContactUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    staff_id: Optional[UUID] = None


@router.post("/")
async def create_contact(
    response: Response,
    request: ContactCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await ContactService.create_contact(request.model_dump(), db)
    response.status_code = result.status_code
    return result


@router.get("/{contact_id}")
async def get_contact(
    response: Response,
    contact_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await ContactService.get_contact_by_id(contact_id, db)
    response.status_code = result.status_code
    return result


@router.patch("/{contact_id}")
async def update_contact(
    response: Response,
    contact_id: UUID,
    request: ContactUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await ContactService.update_contact(contact_id, request.model_dump(exclude_unset=True), db)
    response.status_code = result.status_code
    return result


@router.delete("/{contact_id}")
async def delete_contact(
    response: Response,
    contact_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await ContactService.delete_contact(contact_id, db)
    response.status_code = result.status_code
    return result


@router.get("/")
async def get_all_contacts(
    response: Response,
    page: int = 1,
    limit: int = 10,
    staff_id: UUID = None,
    search: str = None,
    db: AsyncSession = Depends(get_db),
):
    result = await ContactService.get_all_contacts(db, page, limit, staff_id, search)
    response.status_code = result.status_code
    return result
