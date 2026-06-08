from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.entity.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

class Contact(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "contact"

    # Foreign Key
    staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), index=True, nullable=False)
    address = Column(String(255), nullable=True)