from sqlalchemy import Column, String, Boolean, Float, Date, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.entity.base import Base, UUIDPrimaryKeyMixin, TimestampMixin
from app.enums.enums import TicketStage

class Ticket(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ticket"

    # Foreign Keys
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contact.id"), nullable=False)
    call_agent_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=True)
    whatsapp_agent_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=True)

    # State Management
    current_stage = Column(SQLEnum(TicketStage), nullable=False, default=TicketStage.NEW_LEAD)

    # Lead Data
    lead_name = Column(String(255), nullable=False)
    lead_location = Column(String(255), nullable=True)
    course = Column(String(255), nullable=True)
    lead_source = Column(String(100), nullable=True)
    class_mode = Column(String(50), nullable=True)
    budget = Column(Float, nullable=True)
    user_interest = Column(String(255), nullable=True)
    call_back_date = Column(Date, nullable=True)
    objections = Column(String(500), nullable=True)
    for_calling = Column(Boolean, default=False, nullable=False)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=True)