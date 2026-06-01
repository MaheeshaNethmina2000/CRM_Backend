from app.entity.payment import Payment  # Make sure this matches your payment entity file!
from app.repository.base_repository import BaseRepository

class PaymentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Payment)