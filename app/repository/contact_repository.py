from app.entity.contact import Contact
from app.repository.base_repository import BaseRepository

class ContactRepository(BaseRepository):
    def __init__(self):
        super().__init__(Contact)