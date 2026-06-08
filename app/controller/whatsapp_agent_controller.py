from uuid import UUID
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from app.config.database_config import get_db
from app.service.whatsapp_agent_service import WhatsappAgentService
from app.enums.enums import TicketStage, UserRole
from app.util.security import require_roles

router = APIRouter(
    prefix="/v1/api/whatsapp-agent",
    tags=["WhatsApp Agent Operations"],
)

class AgentLeadCreateRequest(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    address: Optional[str] = None
    course: Optional[str] = None
    lead_source: Optional[str] = None
    class_mode: Optional[str] = None
    budget: Optional[float] = None
    user_interest: Optional[str] = None

class AgentLeadUpdateRequest(BaseModel):
    current_stage: Optional[TicketStage] = None
    lead_name: Optional[str] = None
    lead_location: Optional[str] = None
    course: Optional[str] = None
    lead_source: Optional[str] = None
    class_mode: Optional[str] = None
    budget: Optional[float] = None
    user_interest: Optional[str] = None
    for_calling: Optional[bool] = None

@router.post("/leads")
async def create_lead(
        response: Response,
        request: AgentLeadCreateRequest,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(
            require_roles([UserRole.WHATSAPP_AGENT, UserRole.CALL_CENTER_AGENT, UserRole.SYSTEM_ADMIN]))
):
    lead_data = request.model_dump()

    lead_data["creator_id"] = current_user.id
    lead_data["creator_role"] = current_user.role
    lead_data["current_stage"] = TicketStage.NEW_LEAD

    result = await WhatsappAgentService.create_lead(lead_data, db)
    response.status_code = result.status_code
    return result

@router.patch("/leads/{ticket_id}")
async def update_lead(
        response: Response,
        ticket_id: UUID,
        request: AgentLeadUpdateRequest,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(
            require_roles([UserRole.WHATSAPP_AGENT, UserRole.CALL_CENTER_AGENT, UserRole.SYSTEM_ADMIN]))
):
    lead_data = request.model_dump(exclude_unset=True)
    lead_data["updated_by"] = current_user.id
    result = await WhatsappAgentService.update_lead(ticket_id, lead_data, db)
    response.status_code = result.status_code
    return result

@router.patch("/leads/{ticket_id}/mark-for-calling")
async def mark_lead_for_calling(
        response: Response,
        ticket_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(
            require_roles([UserRole.WHATSAPP_AGENT, UserRole.CALL_CENTER_AGENT, UserRole.SYSTEM_ADMIN]))
):
    result = await WhatsappAgentService.mark_for_calling(ticket_id, current_user.id, db)
    response.status_code = result.status_code
    return result