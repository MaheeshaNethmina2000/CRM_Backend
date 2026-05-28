from enum import Enum

class UserRole(str, Enum):
    # Defines the security access control boundaries for internal staff roles
    WHATSAPP_AGENT = "whatsapp_agent"
    CALL_CENTER_AGENT = "call_center_agent"
    PAYMENT_AGENT = "payment_agent"
    SYSTEM_ADMIN = "system_admin"
    MANAGER = "manager"
    CEO = "ceo"

class TicketStage(str, Enum):
    # Represents the sequential pipeline lifecycle states of a student inquiry
    NEW_LEAD = "New Lead"
    QUALIFIED = "Qualified"
    SENT_TO_CALL_CENTRE = "Sent to Call Centre"
    CALLED = "Called"
    CALL_RESCHEDULED = "Call Rescheduled"
    FOLLOW_UP_IN_PROGRESS = "Follow-up in Progress"
    INTERESTED = "Interested"
    SALES_CLOSED = "Sales Closed"
    PAYMENT_PENDING = "Payment Pending"
    PAYMENT_VERIFIED = "Payment Verified"
    ENROLLED = "Enrolled"
    NOT_INTERESTED = "Not Interested"

class PaymentStatus(str, Enum):
    # Tracks the manual review lifecycle of a third-party payment slip submission
    PENDING = "Pending"
    VERIFIED = "Verified"
    REJECTED = "Rejected"