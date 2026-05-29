from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.entity.staff import Staff
from app.repository.staff_repository import StaffRepository
from app.model.generic_response import GenericResponse
from app.model.generic_pagination_response import GenericPaginationResponse
from app.exceptions.exception import NotFoundException, BadRequestException
from app.config.logging_config import get_logger

logger = get_logger(class_name=__name__)
staff_repository = StaffRepository()


class StaffService:

    @classmethod
    async def create_staff(cls, staff_data: dict, db: AsyncSession):
        try:
            logger.info("Create staff process started")
            
            # Check if email already exists
            existing_staff = await staff_repository.get_by_email(staff_data.get("email"), db)
            if existing_staff:
                raise BadRequestException(message="Email already exists")
            
            staff = Staff(**staff_data)
            staff = await staff_repository.save(staff, db)
            
            logger.info(f"Create staff completed with ID: {staff.id}")
            return GenericResponse.success(
                message="Staff created successfully",
                results={"id": str(staff.id), "email": staff.email},
                status_code=201,
            )
        except Exception as e:
            logger.error(f"Error creating staff: {str(e)}")
            if isinstance(e, BadRequestException):
                return GenericResponse.failed(message=e.message, status_code=400, results=[])
            return GenericResponse.failed(
                message=f"Error creating staff: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def get_staff_by_id(cls, staff_id: UUID, db: AsyncSession):
        try:
            logger.info(f"Get staff process started for ID: {staff_id}")
            
            staff = await staff_repository.get_by_id(staff_id, db)
            if not staff:
                raise NotFoundException(message="Staff not found")
            
            logger.info("Get staff process completed")
            return GenericResponse.success(
                message="Staff retrieved successfully",
                results={"id": str(staff.id), "email": staff.email, "role": staff.role.value},
            )
        except Exception as e:
            logger.error(f"Error getting staff: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            return GenericResponse.failed(
                message=f"Error getting staff: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def update_staff(cls, staff_id: UUID, staff_data: dict, db: AsyncSession):
        try:
            logger.info(f"Update staff process started for ID: {staff_id}")
            
            staff = await staff_repository.get_by_id(staff_id, db)
            if not staff:
                raise NotFoundException(message="Staff not found")
            
            for field_name, field_value in staff_data.items():
                if field_value is not None:
                    setattr(staff, field_name, field_value)
            
            staff = await staff_repository.update(staff, db)
            
            logger.info(f"Update staff completed for ID: {staff_id}")
            return GenericResponse.success(
                message="Staff updated successfully",
                results={"id": str(staff.id), "email": staff.email},
            )
        except Exception as e:
            logger.error(f"Error updating staff: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            return GenericResponse.failed(
                message=f"Error updating staff: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def delete_staff(cls, staff_id: UUID, db: AsyncSession):
        try:
            logger.info(f"Delete staff process started for ID: {staff_id}")
            
            staff = await staff_repository.get_by_id(staff_id, db)
            if not staff:
                raise NotFoundException(message="Staff not found")
            
            await db.delete(staff)
            await db.commit()
            
            logger.info(f"Delete staff completed for ID: {staff_id}")
            return GenericResponse.success(
                message="Staff deleted successfully",
                results=[],
            )
        except Exception as e:
            logger.error(f"Error deleting staff: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            return GenericResponse.failed(
                message=f"Error deleting staff: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def get_all_staff(cls, db: AsyncSession, page: int = 1, limit: int = 10, is_active: bool = None):
        try:
            logger.info("Get all staff process started")
            
            page, size, total_pages, total_data_count, staff_list = (
                await staff_repository.get_all_staff_paginated(
                    db=db,
                    page=page,
                    limit=limit,
                    is_active=is_active,
                )
            )
            
            staff_responses = [
                {
                    "id": str(s.id),
                    "email": s.email,
                    "role": s.role.value,
                    "is_active": s.is_active,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in staff_list
            ]
            
            logger.info("Get all staff process completed")
            return GenericPaginationResponse.success(
                message="Staff list retrieved successfully",
                total_records=total_data_count,
                page_number=page,
                page_size=size,
                total_pages=total_pages,
                results=staff_responses,
            )
        except Exception as e:
            logger.error(f"Error getting staff list: {str(e)}")
            return GenericPaginationResponse.failed(
                message=f"Error getting staff list: {str(e)}",
                status_code=500,
                page_number=page,
                page_size=limit,
                results=[],
            )
