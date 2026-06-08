from uuid import UUID
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database_config import get_db
from app.service.call_center_service import CallCenterService
from app.enums.enums import UserRole
from app.util.security import require_roles

router = APIRouter(
    prefix="/v1/api/call-center",
    tags=["Call Center Operations"],
)

@router.patch("/leads/{ticket_id}/mark-answered")
async def mark_call_answered(
        response: Response,
        ticket_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user=Depends(require_roles([UserRole.CALL_CENTER_AGENT]))
):
    result = await CallCenterService.mark_call_answered(ticket_id, current_user.id, db)
    response.status_code = result.status_code
    return result