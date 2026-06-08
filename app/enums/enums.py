from enum import Enum


class UserRole(str, Enum):
    # Internal staff roles defining access control boundaries
    WHATSAPP_AGENT = "whatsapp_agent"
    CALL_CENTER_AGENT = "call_center_agent"
    PAYMENT_AGENT = "payment_agent"
    SYSTEM_ADMIN = "system_admin"
    MANAGER = "manager"
    CEO = "ceo"


class TicketStage(str, Enum):
    NEW_LEAD = "New Lead"
    DRAFTED = "Drafted"
    DETAILS_COMPLETED = "Details Completed"
    QUALIFIED = "Qualified"
    NOT_QUALIFIED = "Not Qualified"
    SENT_TO_CALL_CENTRE = "Sent to Call Centre"
    CALL_ANSWERED = "Call Answered"
    CALL_NOT_ANSWERED = "Call Not Answered"
    CALL_RESCHEDULED = "Call Rescheduled"
    TECHNICAL_FAULT = "Technical Fault"
    WHATSAPP_MESSAGE_SENT = "WhatsApp Message Sent"
    INTERESTED = "Interested"
    NOT_INTERESTED = "Not Interested"
    SALE_CONFIRMED = "Sale Confirmed"
    WAIT_FOR_PAYMENT= "wait for payment"
    CALLED_FOR_PAYMENT = "Called For Payment"
    PAYMENT_COMPLETED = "Payment completed"
    PAYMENT_VERIFIED = "Payment Verified"
    PAYMENT_NOT_VERIFIED = "Payment Not Verified"
    CALLED_FOR_PAYMENT_VERIFICATION = "Called For Payment Verification"
    ENROLLED = "Enrolled"
    LEAD_COMPLETED = "Lead Completed"


class PaymentStatus(str, Enum):
    # manual review lifecycle of a third-party payment slip submission
    PENDING = "Pending"
    VERIFIED = "Verified"
    REJECTED = "Rejected"