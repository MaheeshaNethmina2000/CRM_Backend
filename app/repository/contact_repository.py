from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.entity.contact import Contact
from app.repository.base_repository import BaseRepository


class ContactRepository(BaseRepository):
    def __init__(self):
        super().__init__(Contact)

    async def get_by_phone(self, phone_number: str, db: AsyncSession):
        try:
            query = select(self.model).filter(self.model.phone_number == phone_number)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            raise Exception(f"Failed to get contact by phone. Error: {str(e)}")

    async def get_all_contacts_paginated(
        self,
        db: AsyncSession,
        page: int = 1,
        limit: int = 10,
        staff_id: UUID = None,
        search: str = None,
    ):
        try:
            query = select(self.model)

            if staff_id:
                query = query.filter(self.model.staff_id == staff_id)

            if search:
                query = query.filter(
                    (self.model.first_name.ilike(f"%{search}%")) |
                    (self.model.last_name.ilike(f"%{search}%")) |
                    (self.model.phone_number.ilike(f"%{search}%"))
                )

            total_count_query = select(func.count()).select_from(self.model)
            if staff_id:
                total_count_query = total_count_query.filter(self.model.staff_id == staff_id)
            if search:
                total_count_query = total_count_query.filter(
                    (self.model.first_name.ilike(f"%{search}%")) |
                    (self.model.last_name.ilike(f"%{search}%")) |
                    (self.model.phone_number.ilike(f"%{search}%"))
                )

            total_result = await db.execute(total_count_query)
            total_data_count = total_result.scalar()

            total_pages = (total_data_count + limit - 1) // limit if total_data_count > 0 else 0

            query = query.offset((page - 1) * limit).limit(limit).order_by(self.model.created_at.desc())
            result = await db.execute(query)
            results = result.scalars().all()

            return page, limit, total_pages, total_data_count, results
        except Exception as e:
            raise Exception(f"Failed to get contacts list. Error: {str(e)}")
