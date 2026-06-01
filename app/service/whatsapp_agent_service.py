from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.entity.ticket import Ticket
from app.repository.ticket_repository import TicketRepository
from app.model.generic_response import GenericResponse
from app.exceptions.exception import NotFoundException, BadRequestException
from app.config.logging_config import get_logger
from app.enums.enums import TicketStage
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
            logger.info("WhatsApp Agent creating new contact and lead ticket process started")

            target_stage = payload.get("current_stage", TicketStage.NEW_LEAD)

            # Updated validation to check for 'address' instead of 'lead_location' from the payload
            if target_stage == TicketStage.DETAILS_COMPLETED:
                required_fields = ["course", "address", "budget", "class_mode", "lead_source"]
                missing_fields = [f for f in required_fields if not payload.get(f)]

                if missing_fields:
                    raise BadRequestException(
                        message=f"Cannot mark lead as '{TicketStage.DETAILS_COMPLETED.value}'. Missing required details: {', '.join(missing_fields)}"
                    )

            # --- STEP 1: CREATE THE MASTER CONTACT RECORD ---
            contact_entity_data = {
                "first_name": payload.get("first_name"),
                "last_name": payload.get("last_name"),
                "phone_number": payload.get("phone_number"),
                "address": payload.get("address"),
                "staff_id": payload.get("whatsapp_agent_id")
            }

            new_contact = Contact(**contact_entity_data)
            new_contact = await contact_repository.save(new_contact, db)

            # --- STEP 2: FORMAT DATA & CREATE THE TICKET RECORD ---
            ticket_data = {
                "contact_id": new_contact.id,
                "whatsapp_agent_id": payload.get("whatsapp_agent_id"),

                # Merging fields to match the Ticket database schema
                "lead_name": f"{payload.get('first_name')} {payload.get('last_name')}".strip(),
                "lead_phone": payload.get("phone_number"),
                "lead_location": payload.get("address"),

                # Ticket specific details
                "current_stage": payload.get("current_stage"),
                "course": payload.get("course"),
                "lead_source": payload.get("lead_source"),
                "class_mode": payload.get("class_mode"),
                "budget": payload.get("budget"),
                "user_interest": payload.get("user_interest")
            }

            ticket = Ticket(**ticket_data)
            ticket = await ticket_repository.save(ticket, db)

            # --- STEP 3: CREATE THE ACTIVITY LOG ---
            initial_log = ActivityLog(
                ticket_id=ticket.id,
                action_type="LEAD_CREATED",
                previous_stage=None,
                stage_reached=ticket.current_stage,
                changed_by=payload.get("whatsapp_agent_id"),
                is_system_action=False
            )
            await activity_log_repository.save(initial_log, db)

            logger.info(f"Lead created successfully. Ticket ID: {ticket.id}, Contact ID: {new_contact.id}")
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
                message=f"Error creating lead: {str(e)}",
                status_code=500,
                results=[],
            )

    @classmethod
    async def update_lead(cls, ticket_id: UUID, lead_data: dict, db: AsyncSession):
        try:
            logger.info(f"WhatsApp Agent updating lead process started for Ticket ID: {ticket_id}")

            ticket = await ticket_repository.get_by_id(ticket_id, db)
            if not ticket:
                raise NotFoundException(message="Lead not found")

            new_stage = lead_data.get("current_stage")
            old_stage = ticket.current_stage

            if new_stage == TicketStage.DETAILS_COMPLETED:
                required_fields = ["course", "lead_location", "budget", "class_mode", "lead_source"]
                missing_fields = []

                for f in required_fields:
                    val = lead_data.get(f) if f in lead_data else getattr(ticket, f)
                    if not val:
                        missing_fields.append(f)

                if missing_fields:
                    raise BadRequestException(
                        message=f"Cannot transition lead to '{TicketStage.DETAILS_COMPLETED.value}'. Missing required details: {', '.join(missing_fields)}"
                    )

            if new_stage and new_stage != old_stage:
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
                if field_value is not None:
                    setattr(ticket, field_name, field_value)

            ticket = await ticket_repository.update(ticket, db)

            logger.info(f"Lead updated successfully for Ticket ID: {ticket_id}")
            return GenericResponse.success(
                message="Lead updated successfully",
                results={"ticket_id": str(ticket.id), "lead_name": ticket.lead_name,
                         "current_stage": ticket.current_stage.value},
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