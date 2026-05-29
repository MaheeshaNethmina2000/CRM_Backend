from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.entity.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

class CallDetail(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "call_details"

    # Foreign Keys
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("ticket.id"), nullable=False)
    call_agent_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False)

    Call_outcome = Column(String(255), nullable=False)
    reschedule_datetime = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True)  # Stored in seconds
    agent_note = Column(Text, nullable=True)