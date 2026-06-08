from sqlalchemy import Column, Float, DateTime, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from app.entity.base import Base, UUIDPrimaryKeyMixin, TimestampMixin
from app.enums.enums import PaymentStatus

class Payment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "payments"

    # Foreign Keys
    ticketid = Column(UUID(as_uuid=True), ForeignKey("ticket.id"), nullable=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=True)

    slip_status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    amount = Column(Float, nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    verification_status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    verified_at = Column(DateTime(timezone=True), nullable=True)