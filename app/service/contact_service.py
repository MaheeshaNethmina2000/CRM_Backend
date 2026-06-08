from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.entity.contact import Contact
from app.repository.contact_repository import ContactRepository
from app.model.generic_response import GenericResponse
from app.model.generic_pagination_response import GenericPaginationResponse
from app.exceptions.exception import NotFoundException, BadRequestException
from app.config.logging_config import get_logger

logger = get_logger(class_name=__name__)
contact_repository = ContactRepository()


class ContactService:

    @classmethod
    async def create_contact(cls, contact_data: dict, db: AsyncSession):
        try:
            logger.info("Create contact process started")
            
            contact = Contact(**contact_data)
            contact = await contact_repository.save(contact, db)
            
            logger.info(f"Create contact completed with ID: {contact.id}")
            return GenericResponse.success(
                message="Contact created successfully",
                results={"id": str(contact.id), "phone_number": contact.phone_number},
                status_code=201,
            )
        except Exception as e:
            logger.error(f"Error creating contact: {str(e)}")
            return GenericResponse.failed(
                message=f"Error creating contact: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def get_contact_by_id(cls, contact_id: UUID, db: AsyncSession):
        try:
            logger.info(f"Get contact process started for ID: {contact_id}")
            
            contact = await contact_repository.get_by_id(contact_id, db)
            if not contact:
                raise NotFoundException(message="Contact not found")
            
            logger.info("Get contact process completed")
            return GenericResponse.success(
                message="Contact retrieved successfully",
                results={
                    "id": str(contact.id),
                    "first_name": contact.first_name,
                    "last_name": contact.last_name,
                    "phone_number": contact.phone_number,
                    "address": contact.address,
                },
            )
        except Exception as e:
            logger.error(f"Error getting contact: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            return GenericResponse.failed(
                message=f"Error getting contact: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def update_contact(cls, contact_id: UUID, contact_data: dict, db: AsyncSession):
        try:
            logger.info(f"Update contact process started for ID: {contact_id}")
            
            contact = await contact_repository.get_by_id(contact_id, db)
            if not contact:
                raise NotFoundException(message="Contact not found")
            
            for field_name, field_value in contact_data.items():
                if field_value is not None:
                    setattr(contact, field_name, field_value)
            
            contact = await contact_repository.update(contact, db)
            
            logger.info(f"Update contact completed for ID: {contact_id}")
            return GenericResponse.success(
                message="Contact updated successfully",
                results={"id": str(contact.id), "phone_number": contact.phone_number},
            )
        except Exception as e:
            logger.error(f"Error updating contact: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            return GenericResponse.failed(
                message=f"Error updating contact: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def delete_contact(cls, contact_id: UUID, db: AsyncSession):
        try:
            logger.info(f"Delete contact process started for ID: {contact_id}")
            
            contact = await contact_repository.get_by_id(contact_id, db)
            if not contact:
                raise NotFoundException(message="Contact not found")
            
            await db.delete(contact)
            await db.commit()
            
            logger.info(f"Delete contact completed for ID: {contact_id}")
            return GenericResponse.success(
                message="Contact deleted successfully",
                results=[],
            )
        except Exception as e:
            logger.error(f"Error deleting contact: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            return GenericResponse.failed(
                message=f"Error deleting contact: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def get_all_contacts(cls, db: AsyncSession, page: int = 1, limit: int = 10, staff_id: UUID = None, search: str = None):
        try:
            logger.info("Get all contacts process started")
            
            page, size, total_pages, total_data_count, contacts_list = (
                await contact_repository.get_all_contacts_paginated(
                    db=db,
                    page=page,
                    limit=limit,
                    staff_id=staff_id,
                    search=search,
                )
            )
            
            contact_responses = [
                {
                    "id": str(c.id),
                    "first_name": c.first_name,
                    "last_name": c.last_name,
                    "phone_number": c.phone_number,
                    "address": c.address,
                    "staff_id": str(c.staff_id),
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in contacts_list
            ]
            
            logger.info("Get all contacts process completed")
            return GenericPaginationResponse.success(
                message="Contacts list retrieved successfully",
                total_records=total_data_count,
                page_number=page,
                page_size=size,
                total_pages=total_pages,
                results=contact_responses,
            )
        except Exception as e:
            logger.error(f"Error getting contacts list: {str(e)}")
            return GenericPaginationResponse.failed(
                message=f"Error getting contacts list: {str(e)}",
                status_code=500,
                page_number=page,
                page_size=limit,
                results=[],
            )
