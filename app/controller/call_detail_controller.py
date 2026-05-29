from uuid import UUID
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.config.database_config import get_db
from app.service.call_detail_service import CallDetailService

router = APIRouter(
    prefix="/v1/api/call-details",
    tags=["Call Details"],
)


class CallDetailCreateRequest(BaseModel):
    ticket_id: UUID
    call_agent_id: UUID
    Call_outcome: str
    reschedule_datetime: Optional[datetime] = None
    duration: Optional[int] = None
    agent_note: Optional[str] = None


class CallDetailUpdateRequest(BaseModel):
    Call_outcome: Optional[str] = None
    reschedule_datetime: Optional[datetime] = None
    duration: Optional[int] = None
    agent_note: Optional[str] = None
    call_agent_id: Optional[UUID] = None


@router.post("/")
async def create_call_detail(
    response: Response,
    request: CallDetailCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await CallDetailService.create_call_detail(request.model_dump(), db)
    response.status_code = result.status_code
    return result


@router.get("/{call_detail_id}")
async def get_call_detail(
    response: Response,
    call_detail_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await CallDetailService.get_call_detail_by_id(call_detail_id, db)
    response.status_code = result.status_code
    return result


@router.patch("/{call_detail_id}")
async def update_call_detail(
    response: Response,
    call_detail_id: UUID,
    request: CallDetailUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await CallDetailService.update_call_detail(call_detail_id, request.model_dump(exclude_unset=True), db)
    response.status_code = result.status_code
    return result


@router.delete("/{call_detail_id}")
async def delete_call_detail(
    response: Response,
    call_detail_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await CallDetailService.delete_call_detail(call_detail_id, db)
    response.status_code = result.status_code
    return result


@router.get("/")
async def get_all_call_details(
    response: Response,
    page: int = 1,
    limit: int = 10,
    ticket_id: UUID = None,
    call_agent_id: UUID = None,
    db: AsyncSession = Depends(get_db),
):
    result = await CallDetailService.get_all_call_details(db, page, limit, ticket_id, call_agent_id)
    response.status_code = result.status_code
    return result
