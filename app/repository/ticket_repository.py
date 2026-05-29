from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.entity.ticket import Ticket
from app.repository.base_repository import BaseRepository


class TicketRepository(BaseRepository):
    def __init__(self):
        super().__init__(Ticket)

    async def get_all_tickets_paginated(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 10,
        contact_id: UUID = None,
        current_stage: str = None,
        call_agent_id: UUID = None,
        for_calling: bool = None,
        search: str = None,
    ):
        try:
            query = select(self.model)

            if contact_id:
                query = query.filter(self.model.contact_id == contact_id)

            if current_stage:
                query = query.filter(self.model.current_stage == current_stage)

            if call_agent_id:
                query = query.filter(self.model.call_agent_id == call_agent_id)

            if for_calling is not None:
                query = query.filter(self.model.for_calling == for_calling)

            if search:
                query = query.filter(
                    (self.model.lead_name.ilike(f"%{search}%")) |
                    (self.model.lead_mobilephone.ilike(f"%{search}%")) |
                    (self.model.course.ilike(f"%{search}%"))
                )

            total_count_query = select(func.count()).select_from(self.model)
            if contact_id:
                total_count_query = total_count_query.filter(self.model.contact_id == contact_id)
            if current_stage:
                total_count_query = total_count_query.filter(self.model.current_stage == current_stage)
            if call_agent_id:
                total_count_query = total_count_query.filter(self.model.call_agent_id == call_agent_id)
            if for_calling is not None:
                total_count_query = total_count_query.filter(self.model.for_calling == for_calling)
            if search:
                total_count_query = total_count_query.filter(
                    (self.model.lead_name.ilike(f"%{search}%")) |
                    (self.model.lead_mobilephone.ilike(f"%{search}%")) |
                    (self.model.course.ilike(f"%{search}%"))
                )

            total_result = await db.execute(total_count_query)
            total_data_count = total_result.scalar()

            total_pages = (total_data_count + limit - 1) // limit if total_data_count > 0 else 0

            query = query.offset((page - 1) * limit).limit(limit).order_by(self.model.created_at.desc())
            result = await db.execute(query)
            results = result.scalars().all()

            return page, limit, total_pages, total_data_count, results
        except Exception as e:
            raise Exception(f"Failed to get tickets list. Error: {str(e)}")
