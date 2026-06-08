from app.entity.ticket import Ticket
from app.repository.base_repository import BaseRepository


class TicketRepository(BaseRepository):
    def __init__(self):
        # We pass the Ticket model to the BaseRepository here
        super().__init__(Ticket)

        # You don't even need to write save(), update(), or get_by_id()
    # because BaseRepository already provides them automatically!