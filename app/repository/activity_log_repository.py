from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.entity.activity_log import ActivityLog
from app.repository.base_repository import BaseRepository


class ActivityLogRepository(BaseRepository):
    def __init__(self):
        super().__init__(ActivityLog)

    async def get_history_by_ticket_id(self, ticket_id: UUID, db: AsyncSession):
        """Fetches the complete audit timeline for a single ticket, oldest to newest."""
        try:
            query = select(self.model).filter(
                self.model.ticket_id == ticket_id
            ).order_by(self.model.changed_at.asc())

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise Exception(f"Failed to get activity history. Error: {str(e)}")