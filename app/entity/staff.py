from sqlalchemy import Column, String, Boolean, Enum as SQLEnum
from app.entity.base import Base, UUIDPrimaryKeyMixin, TimestampMixin
from app.enums.enums import UserRole

class Staff(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "staff"

    is_active = Column(Boolean, default=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.WHATSAPP_AGENT)