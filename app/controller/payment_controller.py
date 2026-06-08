from uuid import UUID
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.config.database_config import get_db
from app.service.payment_service import PaymentService
from app.enums.enums import PaymentStatus

router = APIRouter(
    prefix="/v1/api/payments",
    tags=["Payments"],
)


class PaymentCreateRequest(BaseModel):
    ticketid: UUID
    amount: float
    slip_status: PaymentStatus = PaymentStatus.PENDING
    verification_status: PaymentStatus = PaymentStatus.PENDING
    paid_at: Optional[datetime] = None
    verified_by: Optional[UUID] = None
    verified_at: Optional[datetime] = None


class PaymentUpdateRequest(BaseModel):
    amount: Optional[float] = None
    slip_status: Optional[PaymentStatus] = None
    verification_status: Optional[PaymentStatus] = None
    paid_at: Optional[datetime] = None
    verified_by: Optional[UUID] = None
    verified_at: Optional[datetime] = None


@router.post("/")
async def create_payment(
    response: Response,
    request: PaymentCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await PaymentService.create_payment(request.model_dump(), db)
    response.status_code = result.status_code
    return result


@router.get("/{payment_id}")
async def get_payment(
    response: Response,
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await PaymentService.get_payment_by_id(payment_id, db)
    response.status_code = result.status_code
    return result


@router.patch("/{payment_id}")
async def update_payment(
    response: Response,
    payment_id: UUID,
    request: PaymentUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await PaymentService.update_payment(payment_id, request.model_dump(exclude_unset=True), db)
    response.status_code = result.status_code
    return result


@router.delete("/{payment_id}")
async def delete_payment(
    response: Response,
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await PaymentService.delete_payment(payment_id, db)
    response.status_code = result.status_code
    return result


@router.get("/")
async def get_all_payments(
    response: Response,
    page: int = 1,
    limit: int = 10,
    ticketid: UUID = None,
    slip_status: str = None,
    verification_status: str = None,
    verified_by: UUID = None,
    db: AsyncSession = Depends(get_db),
):
    result = await PaymentService.get_all_payments(
        db, page, limit, ticketid, slip_status, verification_status, verified_by
    )
    response.status_code = result.status_code
    return result
