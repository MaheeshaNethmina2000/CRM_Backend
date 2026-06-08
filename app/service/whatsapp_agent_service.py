from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.entity.ticket import Ticket
from app.repository.ticket_repository import TicketRepository
from app.model.generic_response import GenericResponse
from app.exceptions.exception import NotFoundException, BadRequestException
from app.config.logging_config import get_logger
from app.enums.enums import TicketStage, UserRole
from app.entity.activity_log import ActivityLog
from app.repository.activity_log_repository import ActivityLogRepository

from app.entity.contact import Contact
from app.repository.contact_repository import ContactRepository

logger = get_logger(class_name=__name__)
ticket_repository = TicketRepository()
activity_log_repository = ActivityLogRepository()
contact_repository = ContactRepository()

class WhatsappAgentService:

    @classmethod
    async def create_lead(cls, payload: dict, db: AsyncSession):
        try:
            logger.info("Agent creating new contact and lead ticket process started")

            target_stage = payload.get("current_stage")
            creator_id = payload.get("creator_id")
            creator_role = payload.get("creator_role")

            contact_entity_data = {
                "first_name": payload.get("first_name"),
                "last_name": payload.get("last_name"),
                "phone_number": payload.get("phone_number"),
                "address": payload.get("address"),
                "staff_id": creator_id
            }

            new_contact = Contact(**contact_entity_data)
            new_contact = await contact_repository.save(new_contact, db)

            lead_full_name = f"{payload.get('first_name')} {payload.get('last_name')}".strip()

            ticket_data = {
                "contact_id": new_contact.id,
                "lead_name": lead_full_name,
                "lead_location": payload.get("address"),
                "current_stage": target_stage,
                "course": payload.get("course"),
                "lead_source": payload.get("lead_source"),
                "class_mode": payload.get("class_mode"),
                "budget": payload.get("budget"),
                "user_interest": payload.get("user_interest")
            }

            role_string = creator_role.value if hasattr(creator_role, "value") else str(creator_role)

            if role_string == UserRole.CALL_CENTER_AGENT.value:
                ticket_data["call_agent_id"] = creator_id
            elif role_string == UserRole.WHATSAPP_AGENT.value:
                ticket_data["whatsapp_agent_id"] = creator_id

            ticket = Ticket(**ticket_data)
            ticket = await ticket_repository.save(ticket, db)

            initial_log = ActivityLog(
                ticket_id=ticket.id,
                action_type="LEAD_CREATED",
                previous_stage=None,
                stage_reached=ticket.current_stage,
                changed_by=creator_id,
                is_system_action=False
            )
            await activity_log_repository.save(initial_log, db)

            logger.info(f"Lead created successfully by {role_string}. Ticket ID: {ticket.id}")
            return GenericResponse.success(
                message="Contact and Lead created successfully",
                results={
                    "contact_id": str(new_contact.id),
                    "ticket_id": str(ticket.id),
                    "lead_name": ticket.lead_name,
                    "current_stage": ticket.current_stage.value
                },
                status_code=201,
            )
        except Exception as e:
            logger.error(f"Error creating lead: {str(e)}")
            if isinstance(e, BadRequestException):
                return GenericResponse.failed(message=e.message, status_code=400, results=[])
            return GenericResponse.failed(
                message=f"System Error creating lead. Check database constraints: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def update_lead(cls, ticket_id: UUID, lead_data: dict, db: AsyncSession):
        try:
            logger.info(f"Agent updating lead process started for Ticket ID: {ticket_id}")

            ticket = await ticket_repository.get_by_id(ticket_id, db)
            if not ticket:
                raise NotFoundException(message="Lead not found")

            new_stage = lead_data.get("current_stage")
            old_stage = ticket.current_stage

            if new_stage and new_stage != old_stage:
                if new_stage == TicketStage.DETAILS_COMPLETED:
                    required_fields = ["course", "lead_location", "budget", "class_mode", "lead_source"]

                    missing_fields = [f for f in required_fields if not lead_data.get(f, getattr(ticket, f))]

                    if missing_fields:
                        raise BadRequestException(
                            message=f"Cannot transition lead to '{TicketStage.DETAILS_COMPLETED.value}'. Missing required details: {', '.join(missing_fields)}"
                        )

                    lead_data["for_calling"] = True

                stage_log = ActivityLog(
                    ticket_id=ticket.id,
                    action_type="STAGE_CHANGE",
                    previous_stage=old_stage,
                    stage_reached=new_stage,
                    changed_by=lead_data.get("updated_by"),
                    is_system_action=False
                )
                await activity_log_repository.save(stage_log, db)

            for field_name, field_value in lead_data.items():
                setattr(ticket, field_name, field_value)

            ticket = await ticket_repository.update(ticket, db)

            logger.info(f"Lead updated successfully for Ticket ID: {ticket_id}")
            return GenericResponse.success(
                message="Lead updated successfully",
                results={
                    "ticket_id": str(ticket.id),
                    "lead_name": ticket.lead_name,
                    "current_stage": ticket.current_stage.value,
                    "for_calling": ticket.for_calling
                },
            )
        except Exception as e:
            logger.error(f"Error updating lead: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            elif isinstance(e, BadRequestException):
                return GenericResponse.failed(message=e.message, status_code=400, results=[])
            return GenericResponse.failed(
                message=f"Error updating lead: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def mark_for_calling(cls, ticket_id: UUID, agent_id: UUID, db: AsyncSession):
        try:
            logger.info(f"Agent marking lead for calling. Ticket ID: {ticket_id}")

            ticket = await ticket_repository.get_by_id(ticket_id, db)
            if not ticket:
                raise NotFoundException(message="Lead not found")

            if ticket.for_calling and ticket.current_stage == TicketStage.SENT_TO_CALL_CENTRE:
                return GenericResponse.success(
                    message="Lead is already marked for calling and in the Call Center queue",
                    results={"ticket_id": str(ticket.id), "for_calling": ticket.for_calling,
                             "current_stage": ticket.current_stage.value}
                )

            old_stage = ticket.current_stage

            ticket.for_calling = True
            ticket.current_stage = TicketStage.SENT_TO_CALL_CENTRE
            ticket.updated_by = agent_id

            action_log = ActivityLog(
                ticket_id=ticket.id,
                action_type="MARKED_FOR_CALLING",
                previous_stage=old_stage,
                stage_reached=TicketStage.SENT_TO_CALL_CENTRE,
                changed_by=agent_id,
                is_system_action=False
            )
            await activity_log_repository.save(action_log, db)

            ticket = await ticket_repository.update(ticket, db)

            logger.info(f"Lead successfully marked for calling and stage updated. Ticket ID: {ticket_id}")
            return GenericResponse.success(
                message="Lead successfully marked for calling",
                results={
                    "ticket_id": str(ticket.id),
                    "for_calling": ticket.for_calling,
                    "current_stage": ticket.current_stage.value
                }
            )
        except Exception as e:
            logger.error(f"Error marking lead for calling: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            return GenericResponse.failed(
                message=f"Error marking lead for calling: {str(e)}",
                status_code=500,
                results=[],
            )