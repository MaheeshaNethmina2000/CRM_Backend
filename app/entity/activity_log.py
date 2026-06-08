from sqlalchemy import Column, DateTime, ForeignKey, Enum as SAEnum, Text, Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

# Import Base AND your UUIDPrimaryKeyMixin
from app.entity.base import Base, UUIDPrimaryKeyMixin
from app.enums.enums import TicketStage


# Inherit from both Base and the Mixin
class ActivityLog(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "activity_logs"

    ticket_id = Column(UUID(as_uuid=True),ForeignKey("ticket.id", ondelete="CASCADE"),nullable=False)
    action_type = Column(String,nullable=False)
    stage_reached = Column(SAEnum(TicketStage),nullable=False)
    note = Column(Text,nullable=True)
    is_system_action = Column(Boolean,default=False,nullable=False)
    previous_stage = Column(SAEnum(TicketStage),nullable=True)
    changed_by = Column(UUID(as_uuid=True),ForeignKey("staff.id", ondelete="SET NULL"),nullable=True)
    changed_at = Column(DateTime(timezone=True),server_default=func.now())