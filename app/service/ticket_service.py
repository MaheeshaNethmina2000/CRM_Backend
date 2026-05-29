from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.entity.ticket import Ticket
from app.repository.ticket_repository import TicketRepository
from app.model.generic_response import GenericResponse
from app.model.generic_pagination_response import GenericPaginationResponse
from app.exceptions.exception import NotFoundException
from app.config.logging_config import get_logger

logger = get_logger(class_name=__name__)
ticket_repository = TicketRepository()


class TicketService:

    @classmethod
    async def create_ticket(cls, ticket_data: dict, db: AsyncSession):
        try:
            logger.info("Create ticket process started")
            
            ticket = Ticket(**ticket_data)
            ticket = await ticket_repository.save(ticket, db)
            
            logger.info(f"Create ticket completed with ID: {ticket.id}")
            return GenericResponse.success(
                message="Ticket created successfully",
                results={"id": str(ticket.id), "lead_name": ticket.lead_name},
                status_code=201,
            )
        except Exception as e:
            logger.error(f"Error creating ticket: {str(e)}")
            return GenericResponse.failed(
                message=f"Error creating ticket: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def get_ticket_by_id(cls, ticket_id: UUID, db: AsyncSession):
        try:
            logger.info(f"Get ticket process started for ID: {ticket_id}")
            
            ticket = await ticket_repository.get_by_id(ticket_id, db)
            if not ticket:
                raise NotFoundException(message="Ticket not found")
            
            logger.info("Get ticket process completed")
            return GenericResponse.success(
                message="Ticket retrieved successfully",
                results={
                    "id": str(ticket.id),
                    "contact_id": str(ticket.contact_id),
                    "lead_name": ticket.lead_name,
                    "lead_mobilephone": ticket.lead_mobilephone,
                    "current_stage": ticket.current_stage.value,
                    "course": ticket.course,
                    "budget": ticket.budget,
                },
            )
        except Exception as e:
            logger.error(f"Error getting ticket: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            return GenericResponse.failed(
                message=f"Error getting ticket: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def update_ticket(cls, ticket_id: UUID, ticket_data: dict, db: AsyncSession):
        try:
            logger.info(f"Update ticket process started for ID: {ticket_id}")
            
            ticket = await ticket_repository.get_by_id(ticket_id, db)
            if not ticket:
                raise NotFoundException(message="Ticket not found")
            
            for field_name, field_value in ticket_data.items():
                if field_value is not None:
                    setattr(ticket, field_name, field_value)
            
            ticket = await ticket_repository.update(ticket, db)
            
            logger.info(f"Update ticket completed for ID: {ticket_id}")
            return GenericResponse.success(
                message="Ticket updated successfully",
                results={"id": str(ticket.id), "lead_name": ticket.lead_name},
            )
        except Exception as e:
            logger.error(f"Error updating ticket: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            return GenericResponse.failed(
                message=f"Error updating ticket: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def delete_ticket(cls, ticket_id: UUID, db: AsyncSession):
        try:
            logger.info(f"Delete ticket process started for ID: {ticket_id}")
            
            ticket = await ticket_repository.get_by_id(ticket_id, db)
            if not ticket:
                raise NotFoundException(message="Ticket not found")
            
            await db.delete(ticket)
            await db.commit()
            
            logger.info(f"Delete ticket completed for ID: {ticket_id}")
            return GenericResponse.success(
                message="Ticket deleted successfully",
                results=[],
            )
        except Exception as e:
            logger.error(f"Error deleting ticket: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            return GenericResponse.failed(
                message=f"Error deleting ticket: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def get_all_tickets(
        cls,
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
            logger.info("Get all tickets process started")
            
            page, size, total_pages, total_data_count, tickets_list = (
                await ticket_repository.get_all_tickets_paginated(
                    db=db,
                    page=page,
                    limit=limit,
                    contact_id=contact_id,
                    current_stage=current_stage,
                    call_agent_id=call_agent_id,
                    for_calling=for_calling,
                    search=search,
                )
            )
            
            ticket_responses = [
                {
                    "id": str(t.id),
                    "contact_id": str(t.contact_id),
                    "lead_name": t.lead_name,
                    "lead_mobilephone": t.lead_mobilephone,
                    "current_stage": t.current_stage.value,
                    "course": t.course,
                    "budget": t.budget,
                    "for_calling": t.for_calling,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                }
                for t in tickets_list
            ]
            
            logger.info("Get all tickets process completed")
            return GenericPaginationResponse.success(
                message="Tickets list retrieved successfully",
                total_records=total_data_count,
                page_number=page,
                page_size=size,
                total_pages=total_pages,
                results=ticket_responses,
            )
        except Exception as e:
            logger.error(f"Error getting tickets list: {str(e)}")
            return GenericPaginationResponse.failed(
                message=f"Error getting tickets list: {str(e)}",
                status_code=500,
                page_number=page,
                page_size=limit,
                results=[],
            )
