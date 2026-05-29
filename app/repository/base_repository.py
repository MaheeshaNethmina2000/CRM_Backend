from abc import ABC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.logging_config import get_logger
from app.exceptions.exception import DbOperationException

logger = get_logger(class_name=__name__)


class BaseRepository(ABC):

    def __init__(self, model):
        self.model = model

    @classmethod
    async def save(cls, entity, db: AsyncSession):
        try:
            db.add(entity)
            await db.commit()
            await db.refresh(entity)
            return entity
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to save entity to database. Error: {str(e)}")
            raise DbOperationException(message="Unable to save the entity.")

    async def get_by_id(self, _id, db: AsyncSession):
        try:
            query = select(self.model).filter(self.model.id == _id)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get entity by id. Error: {str(e)}")
            raise DbOperationException(message="Unable to get the entity.")

    @classmethod
    async def update(cls, entity, db: AsyncSession):
        try:
            await db.commit()
            await db.refresh(entity)
            return entity
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update entity. Error: {str(e)}")
            raise DbOperationException(message="Unable to update the entity.")
