from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.entity.staff import Staff
from app.repository.base_repository import BaseRepository


class StaffRepository(BaseRepository):
    def __init__(self):
        super().__init__(Staff)

    async def get_by_email(self, email: str, db: AsyncSession):
        try:
            query = select(self.model).filter(self.model.email == email)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise Exception(f"Failed to get staff by email. Error: {str(e)}")

    async def get_all_staff_paginated(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 10,
        is_active: bool = None,
    ):
        try:
            query = select(self.model)

            if is_active is not None:
                query = query.filter(self.model.is_active == is_active)

            total_count_query = select(func.count()).select_from(self.model)
            if is_active is not None:
                total_count_query = total_count_query.filter(self.model.is_active == is_active)

            total_result = await db.execute(total_count_query)
            total_data_count = total_result.scalar()

            total_pages = (total_data_count + limit - 1) // limit if total_data_count > 0 else 0

            query = query.offset((page - 1) * limit).limit(limit).order_by(self.model.created_at.desc())
            result = await db.execute(query)
            results = result.scalars().all()

            return page, limit, total_pages, total_data_count, results
        except Exception as e:
            raise Exception(f"Failed to get staff list. Error: {str(e)}")
