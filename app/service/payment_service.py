from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.entity.payment import Payment
from app.repository.payment_repository import PaymentRepository
from app.model.generic_response import GenericResponse
from app.model.generic_pagination_response import GenericPaginationResponse
from app.exceptions.exception import NotFoundException
from app.config.logging_config import get_logger

logger = get_logger(class_name=__name__)
payment_repository = PaymentRepository()


class PaymentService:

    @classmethod
    async def create_payment(cls, payment_data: dict, db: AsyncSession):
        try:
            logger.info("Create payment process started")
            
            payment = Payment(**payment_data)
            payment = await payment_repository.save(payment, db)
            
            logger.info(f"Create payment completed with ID: {payment.id}")
            return GenericResponse.success(
                message="Payment created successfully",
                results={"id": str(payment.id), "amount": payment.amount},
                status_code=201,
            )
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            return GenericResponse.failed(
                message=f"Error creating payment: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def get_payment_by_id(cls, payment_id: UUID, db: AsyncSession):
        try:
            logger.info(f"Get payment process started for ID: {payment_id}")
            
            payment = await payment_repository.get_by_id(payment_id, db)
            if not payment:
                raise NotFoundException(message="Payment not found")
            
            logger.info("Get payment process completed")
            return GenericResponse.success(
                message="Payment retrieved successfully",
                results={
                    "id": str(payment.id),
                    "ticketid": str(payment.ticketid),
                    "amount": payment.amount,
                    "slip_status": payment.slip_status.value,
                    "verification_status": payment.verification_status.value,
                },
            )
        except Exception as e:
            logger.error(f"Error getting payment: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            return GenericResponse.failed(
                message=f"Error getting payment: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def update_payment(cls, payment_id: UUID, payment_data: dict, db: AsyncSession):
        try:
            logger.info(f"Update payment process started for ID: {payment_id}")
            
            payment = await payment_repository.get_by_id(payment_id, db)
            if not payment:
                raise NotFoundException(message="Payment not found")
            
            for field_name, field_value in payment_data.items():
                if field_value is not None:
                    setattr(payment, field_name, field_value)
            
            payment = await payment_repository.update(payment, db)
            
            logger.info(f"Update payment completed for ID: {payment_id}")
            return GenericResponse.success(
                message="Payment updated successfully",
                results={"id": str(payment.id), "amount": payment.amount},
            )
        except Exception as e:
            logger.error(f"Error updating payment: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            return GenericResponse.failed(
                message=f"Error updating payment: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def delete_payment(cls, payment_id: UUID, db: AsyncSession):
        try:
            logger.info(f"Delete payment process started for ID: {payment_id}")
            
            payment = await payment_repository.get_by_id(payment_id, db)
            if not payment:
                raise NotFoundException(message="Payment not found")
            
            await db.delete(payment)
            await db.commit()
            
            logger.info(f"Delete payment completed for ID: {payment_id}")
            return GenericResponse.success(
                message="Payment deleted successfully",
                results=[],
            )
        except Exception as e:
            logger.error(f"Error deleting payment: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            return GenericResponse.failed(
                message=f"Error deleting payment: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def get_all_payments(
        cls,
        db: AsyncSession,
        page: int = 1,
        limit: int = 10,
        ticketid: UUID = None,
        slip_status: str = None,
        verification_status: str = None,
        verified_by: UUID = None,
    ):
        try:
            logger.info("Get all payments process started")
            
            page, size, total_pages, total_data_count, payments_list = (
                await payment_repository.get_all_payments_paginated(
                    db=db,
                    page=page,
                    limit=limit,
                    ticketid=ticketid,
                    slip_status=slip_status,
                    verification_status=verification_status,
                    verified_by=verified_by,
                )
            )
            
            payment_responses = [
                {
                    "id": str(p.id),
                    "ticketid": str(p.ticketid),
                    "amount": p.amount,
                    "slip_status": p.slip_status.value,
                    "verification_status": p.verification_status.value,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in payments_list
            ]
            
            logger.info("Get all payments process completed")
            return GenericPaginationResponse.success(
                message="Payments list retrieved successfully",
                total_records=total_data_count,
                page_number=page,
                page_size=size,
                total_pages=total_pages,
                results=payment_responses,
            )
        except Exception as e:
            logger.error(f"Error getting payments list: {str(e)}")
            return GenericPaginationResponse.failed(
                message=f"Error getting payments list: {str(e)}",
                status_code=500,
                page_number=page,
                page_size=limit,
                results=[],
            )
