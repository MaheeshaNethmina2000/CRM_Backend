from uuid import UUID
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.config.database_config import get_db
from app.service.ticket_service import TicketService
from app.enums.enums import TicketStage

router = APIRouter(
    prefix="/v1/api/tickets",
    tags=["Tickets"],
)


class TicketCreateRequest(BaseModel):
    contact_id: UUID
    lead_name: str
    lead_mobilephone: str
    lead_location: Optional[str] = None
    course: Optional[str] = None
    lead_source: Optional[str] = None
    class_mode: Optional[str] = None
    budget: Optional[float] = None
    user_interest: Optional[str] = None
    call_back_date: Optional[date] = None
    objections: Optional[str] = None
    for_calling: bool = False
    call_agent_id: Optional[UUID] = None
    whatsapp_agent_id: Optional[UUID] = None


class TicketUpdateRequest(BaseModel):
    current_stage: Optional[TicketStage] = None
    lead_name: Optional[str] = None
    lead_mobilephone: Optional[str] = None
    lead_location: Optional[str] = None
    course: Optional[str] = None
    lead_source: Optional[str] = None
    class_mode: Optional[str] = None
    budget: Optional[float] = None
    user_interest: Optional[str] = None
    call_back_date: Optional[date] = None
    objections: Optional[str] = None
    for_calling: Optional[bool] = None
    call_agent_id: Optional[UUID] = None
    whatsapp_agent_id: Optional[UUID] = None
    updated_by: Optional[UUID] = None


@router.post("/")
async def create_ticket(
    response: Response,
    request: TicketCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await TicketService.create_ticket(request.model_dump(), db)
    response.status_code = result.status_code
    return result


@router.get("/{ticket_id}")
async def get_ticket(
    response: Response,
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await TicketService.get_ticket_by_id(ticket_id, db)
    response.status_code = result.status_code
    return result


@router.patch("/{ticket_id}")
async def update_ticket(
    response: Response,
    ticket_id: UUID,
    request: TicketUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await TicketService.update_ticket(ticket_id, request.model_dump(exclude_unset=True), db)
    response.status_code = result.status_code
    return result


@router.delete("/{ticket_id}")
async def delete_ticket(
    response: Response,
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await TicketService.delete_ticket(ticket_id, db)
    response.status_code = result.status_code
    return result


@router.get("/")
async def get_all_tickets(
    response: Response,
    page: int = 1,
    limit: int = 10,
    contact_id: UUID = None,
    current_stage: str = None,
    call_agent_id: UUID = None,
    for_calling: bool = None,
    search: str = None,
    db: AsyncSession = Depends(get_db),
):
    result = await TicketService.get_all_tickets(
        db, page, limit, contact_id, current_stage, call_agent_id, for_calling, search
    )
    response.status_code = result.status_code
    return result
