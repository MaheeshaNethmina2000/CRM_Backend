from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.entity.call_detail import CallDetail
from app.repository.base_repository import BaseRepository


class CallDetailRepository(BaseRepository):
    def __init__(self):
        super().__init__(CallDetail)

    async def get_all_call_details_paginated(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 10,
        ticket_id: UUID = None,
        call_agent_id: UUID = None,
    ):
        try:
            query = select(self.model)

            if ticket_id:
                query = query.filter(self.model.ticket_id == ticket_id)

            if call_agent_id:
                query = query.filter(self.model.call_agent_id == call_agent_id)

            total_count_query = select(func.count()).select_from(self.model)
            if ticket_id:
                total_count_query = total_count_query.filter(self.model.ticket_id == ticket_id)
            if call_agent_id:
                total_count_query = total_count_query.filter(self.model.call_agent_id == call_agent_id)

            total_result = await db.execute(total_count_query)
            total_data_count = total_result.scalar()

            total_pages = (total_data_count + limit - 1) // limit if total_data_count > 0 else 0

            query = query.offset((page - 1) * limit).limit(limit).order_by(self.model.created_at.desc())
            result = await db.execute(query)
            results = result.scalars().all()

            return page, limit, total_pages, total_data_count, results
        except Exception as e:
            raise Exception(f"Failed to get call details list. Error: {str(e)}")
