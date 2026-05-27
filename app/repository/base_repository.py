from abc import ABC

from app.config.logging_config import get_logger
from app.exceptions.exception import DbOperationException

logger = get_logger(class_name=__name__)


class BaseRepository(ABC):

    def __init__(self, model):
        self.model = model

    @classmethod
    def save(cls, entity, db):
        try:
            db.add(entity)
            db.commit()
            db.refresh(entity)
            return entity
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save entity to database. Error: {str(e)}")
            raise DbOperationException(message="Unable to save the entity.")

    def get_by_id(self, _id, db):
        try:
            return db.query(self.model).filter(self.model.id == _id).first()
        except Exception as e:
            logger.error(f"Failed to get entity by id. Error: {str(e)}")
            raise DbOperationException(message="Unable to get the entity.")

    @classmethod
    def update(cls, entity, db):
        try:
            db.commit()
            db.refresh(entity)
            return entity
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update entity. Error: {str(e)}")
            raise DbOperationException(message="Unable to update the entity.")
