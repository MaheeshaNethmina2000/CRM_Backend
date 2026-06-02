from uuid import UUID
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.config.database_config import get_db
from app.service.whatsapp_agent_service import WhatsappAgentService
from app.enums.enums import TicketStage, UserRole
from app.util.security import require_roles, get_current_user

router = APIRouter(
    prefix="/v1/api/whatsapp-agent",
    tags=["WhatsApp Agent Operations"],
)


class AgentLeadCreateRequest(BaseModel):
    # --- EXPLICIT CONTACT DETAILS ---
    first_name: str
    last_name: str
    phone_number: str
    address: Optional[str] = None

    # --- TICKET SPECIFIC DETAILS ---
    # 'current_stage' is REMOVED from here. The backend automatically forces it.
    course: Optional[str] = None
    lead_source: Optional[str] = None
    class_mode: Optional[str] = None
    budget: Optional[float] = None
    user_interest: Optional[str] = None


class AgentLeadUpdateRequest(BaseModel):
    # 'current_stage' stays here because updates WILL change the stage!
    current_stage: Optional[TicketStage] = None
    lead_name: Optional[str] = None
    lead_phone: Optional[str] = None
    lead_location: Optional[str] = None
    course: Optional[str] = None
    lead_source: Optional[str] = None
    class_mode: Optional[str] = None
    budget: Optional[float] = None
    user_interest: Optional[str] = None


@router.post("/leads")
async def create_lead(
        response: Response,
        request: AgentLeadCreateRequest,
        db: AsyncSession = Depends(get_db),
        # Lock down to WhatsApp Agents and Admins
        current_user=Depends(require_roles([UserRole.WHATSAPP_AGENT, UserRole.SYSTEM_ADMIN]))
):
    lead_data = request.model_dump()

    # --- AUTOMATIC SYSTEM INJECTIONS ---
    # 1. Automatically track which agent created this lead securely via their JWT token
    lead_data["whatsapp_agent_id"] = current_user.id

    # 2. Automatically force the creation stage to NEW_LEAD
    lead_data["current_stage"] = TicketStage.NEW_LEAD
    # -----------------------------------

    result = await WhatsappAgentService.create_lead(lead_data, db)
    response.status_code = result.status_code
    return result


@router.patch("/leads/{ticket_id}")
async def update_lead(
        response: Response,
        ticket_id: UUID,
        request: AgentLeadUpdateRequest,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(require_roles([UserRole.WHATSAPP_AGENT, UserRole.SYSTEM_ADMIN]))
):
    lead_data = request.model_dump(exclude_unset=True)

    # Track exactly who made this update for the audit logs
    lead_data["updated_by"] = current_user.id

    result = await WhatsappAgentService.update_lead(ticket_id, lead_data, db)
    response.status_code = result.status_code
    return result