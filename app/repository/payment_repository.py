from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.entity.payment import Payment
from app.repository.base_repository import BaseRepository


class PaymentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Payment)

    async def get_all_payments_paginated(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 10,
        ticketid: UUID = None,
        slip_status: str = None,
        verification_status: str = None,
        verified_by: UUID = None,
    ):
        try:
            query = select(self.model)

            if ticketid:
                query = query.filter(self.model.ticketid == ticketid)

            if slip_status:
                query = query.filter(self.model.slip_status == slip_status)

            if verification_status:
                query = query.filter(self.model.verification_status == verification_status)

            if verified_by:
                query = query.filter(self.model.verified_by == verified_by)

            total_count_query = select(func.count()).select_from(self.model)
            if ticketid:
                total_count_query = total_count_query.filter(self.model.ticketid == ticketid)
            if slip_status:
                total_count_query = total_count_query.filter(self.model.slip_status == slip_status)
            if verification_status:
                total_count_query = total_count_query.filter(self.model.verification_status == verification_status)
            if verified_by:
                total_count_query = total_count_query.filter(self.model.verified_by == verified_by)

            total_result = await db.execute(total_count_query)
            total_data_count = total_result.scalar()

            total_pages = (total_data_count + limit - 1) // limit if total_data_count > 0 else 0

            query = query.offset((page - 1) * limit).limit(limit).order_by(self.model.created_at.desc())
            result = await db.execute(query)
            results = result.scalars().all()

            return page, limit, total_pages, total_data_count, results
        except Exception as e:
            raise Exception(f"Failed to get payments list. Error: {str(e)}")
