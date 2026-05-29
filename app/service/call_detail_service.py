from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.entity.call_detail import CallDetail
from app.repository.call_detail_repository import CallDetailRepository
from app.model.generic_response import GenericResponse
from app.model.generic_pagination_response import GenericPaginationResponse
from app.exceptions.exception import NotFoundException
from app.config.logging_config import get_logger

logger = get_logger(class_name=__name__)
call_detail_repository = CallDetailRepository()


class CallDetailService:

    @classmethod
    async def create_call_detail(cls, call_detail_data: dict, db: AsyncSession):
        try:
            logger.info("Create call detail process started")
            
            call_detail = CallDetail(**call_detail_data)
            call_detail = await call_detail_repository.save(call_detail, db)
            
            logger.info(f"Create call detail completed with ID: {call_detail.id}")
            return GenericResponse.success(
                message="Call detail created successfully",
                results={"id": str(call_detail.id), "Call_outcome": call_detail.Call_outcome},
                status_code=201,
            )
        except Exception as e:
            logger.error(f"Error creating call detail: {str(e)}")
            return GenericResponse.failed(
                message=f"Error creating call detail: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def get_call_detail_by_id(cls, call_detail_id: UUID, db: AsyncSession):
        try:
            logger.info(f"Get call detail process started for ID: {call_detail_id}")
            
            call_detail = await call_detail_repository.get_by_id(call_detail_id, db)
            if not call_detail:
                raise NotFoundException(message="Call detail not found")
            
            logger.info("Get call detail process completed")
            return GenericResponse.success(
                message="Call detail retrieved successfully",
                results={
                    "id": str(call_detail.id),
                    "ticket_id": str(call_detail.ticket_id),
                    "call_agent_id": str(call_detail.call_agent_id),
                    "Call_outcome": call_detail.Call_outcome,
                    "duration": call_detail.duration,
                },
            )
        except Exception as e:
            logger.error(f"Error getting call detail: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            return GenericResponse.failed(
                message=f"Error getting call detail: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def update_call_detail(cls, call_detail_id: UUID, call_detail_data: dict, db: AsyncSession):
        try:
            logger.info(f"Update call detail process started for ID: {call_detail_id}")
            
            call_detail = await call_detail_repository.get_by_id(call_detail_id, db)
            if not call_detail:
                raise NotFoundException(message="Call detail not found")
            
            for field_name, field_value in call_detail_data.items():
                if field_value is not None:
                    setattr(call_detail, field_name, field_value)
            
            call_detail = await call_detail_repository.update(call_detail, db)
            
            logger.info(f"Update call detail completed for ID: {call_detail_id}")
            return GenericResponse.success(
                message="Call detail updated successfully",
                results={"id": str(call_detail.id), "Call_outcome": call_detail.Call_outcome},
            )
        except Exception as e:
            logger.error(f"Error updating call detail: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            return GenericResponse.failed(
                message=f"Error updating call detail: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def delete_call_detail(cls, call_detail_id: UUID, db: AsyncSession):
        try:
            logger.info(f"Delete call detail process started for ID: {call_detail_id}")
            
            call_detail = await call_detail_repository.get_by_id(call_detail_id, db)
            if not call_detail:
                raise NotFoundException(message="Call detail not found")
            
            await db.delete(call_detail)
            await db.commit()
            
            logger.info(f"Delete call detail completed for ID: {call_detail_id}")
            return GenericResponse.success(
                message="Call detail deleted successfully",
                results=[],
            )
        except Exception as e:
            logger.error(f"Error deleting call detail: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            return GenericResponse.failed(
                message=f"Error deleting call detail: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def get_all_call_details(
        cls,
        db: AsyncSession,
        page: int = 1,
        limit: int = 10,
        ticket_id: UUID = None,
        call_agent_id: UUID = None,
    ):
        try:
            logger.info("Get all call details process started")
            
            page, size, total_pages, total_data_count, call_details_list = (
                await call_detail_repository.get_all_call_details_paginated(
                    db=db,
                    page=page,
                    limit=limit,
                    ticket_id=ticket_id,
                    call_agent_id=call_agent_id,
                )
            )
            
            call_detail_responses = [
                {
                    "id": str(cd.id),
                    "ticket_id": str(cd.ticket_id),
                    "call_agent_id": str(cd.call_agent_id),
                    "Call_outcome": cd.Call_outcome,
                    "duration": cd.duration,
                    "created_at": cd.created_at.isoformat() if cd.created_at else None,
                }
                for cd in call_details_list
            ]
            
            logger.info("Get all call details process completed")
            return GenericPaginationResponse.success(
                message="Call details list retrieved successfully",
                total_records=total_data_count,
                page_number=page,
                page_size=size,
                total_pages=total_pages,
                results=call_detail_responses,
            )
        except Exception as e:
            logger.error(f"Error getting call details list: {str(e)}")
            return GenericPaginationResponse.failed(
                message=f"Error getting call details list: {str(e)}",
                status_code=500,
                page_number=page,
                page_size=limit,
                results=[],
            )
