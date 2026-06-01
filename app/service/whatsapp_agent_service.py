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

logger = get_logger(class_name=__name__)
ticket_repository = TicketRepository()
activity_log_repository = ActivityLogRepository()

class WhatsappAgentService:

    @classmethod
    async def create_lead(cls, lead_data: dict, db: AsyncSession):
        try:
            logger.info(f"WhatsApp Agent creating lead process started for contact: {lead_data.get('contact_id')}")

            target_stage = lead_data.get("current_stage", TicketStage.NEW_LEAD)

            if target_stage == TicketStage.DETAILS_COMPLETED:
                required_fields = ["course", "lead_location", "budget", "class_mode", "lead_source"]
                missing_fields = [f for f in required_fields if not lead_data.get(f)]

                if missing_fields:
                    raise BadRequestException(
                        message=f"Cannot mark lead as '{TicketStage.DETAILS_COMPLETED.value}'. Missing required details: {', '.join(missing_fields)}"
                    )

            # Save the new ticket
            ticket = Ticket(**lead_data)
            ticket = await ticket_repository.save(ticket, db)

            initial_log = ActivityLog(
                ticket_id=ticket.id,
                action_type="LEAD_CREATED",
                previous_stage=None,
                stage_reached=ticket.current_stage,
                changed_by=lead_data.get("whatsapp_agent_id"),
                is_system_action=False
            )
            await activity_log_repository.save(initial_log, db)

            logger.info(f"Lead created successfully with Ticket ID: {ticket.id}")
            return GenericResponse.success(
                message="Lead created successfully",
                results={
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
            old_stage = ticket.current_stage # Capture the current stage before updating

            #Validating Stage Upgrades
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

            # --- AUTOMATED AUDIT TRAIL ---
            # Only drop a receipt if the stage is actually changing!
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
            # -----------------------------

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