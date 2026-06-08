from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.entity.ticket import Ticket
from app.entity.call_detail import CallDetail
from app.entity.activity_log import ActivityLog
from app.repository.ticket_repository import TicketRepository
from app.repository.base_repository import BaseRepository
from app.repository.activity_log_repository import ActivityLogRepository
from app.model.generic_response import GenericResponse
from app.exceptions.exception import NotFoundException
from app.config.logging_config import get_logger
from app.enums.enums import TicketStage

logger = get_logger(class_name=__name__)
ticket_repository = TicketRepository()
activity_log_repository = ActivityLogRepository()
call_detail_repository = BaseRepository(CallDetail)


class CallCenterService:

    @classmethod
    async def mark_call_answered(cls, ticket_id: UUID, agent_id: UUID, db: AsyncSession):
        try:
            logger.info(f"Call Center Agent marking ticket {ticket_id} as answered.")

            ticket = await ticket_repository.get_by_id(ticket_id, db)
            if not ticket:
                raise NotFoundException(message="Lead not found")

            # 1. Save exact relative IDs into call_details
            call_detail = CallDetail(
                ticket_id=ticket.id,
                call_agent_id=agent_id,
                Call_outcome="Answered"
            )
            await call_detail_repository.save(call_detail, db)

            # 2. Update strict columns inside the ticket schema
            ticket.current_stage = TicketStage.CALL_ANSWERED
            ticket.call_agent_id = agent_id
            ticket.updated_by = agent_id

            ticket = await ticket_repository.update(ticket, db)

            # 3. Record clean history trace inside audit logging
            action_log = ActivityLog(
                ticket_id=ticket.id,
                action_type="MARKED AS CALLED",
                previous_stage=TicketStage.SENT_TO_CALL_CENTRE,
                stage_reached=TicketStage.CALL_ANSWERED,
                changed_by=agent_id,
                is_system_action=False
            )
            await activity_log_repository.save(action_log, db)

            logger.info(f"Successfully marked ticket {ticket_id} as answered.")
            return GenericResponse.success(
                message="Call marked as answered successfully",
                results={
                    "ticket_id": str(ticket.id),
                    "current_stage": ticket.current_stage.value
                }
            )
        except Exception as e:
            logger.error(f"Error marking call as answered: {str(e)}")
            if isinstance(e, NotFoundException):
                return GenericResponse.failed(message=e.message, status_code=404, results=[])
            return GenericResponse.failed(
                message=f"System error while marking call as answered: {str(e)}",
                status_code=500,
                results=[],
            )