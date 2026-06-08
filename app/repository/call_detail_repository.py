from app.entity.call_detail import CallDetail
from app.repository.base_repository import BaseRepository

class CallDetailRepository(BaseRepository):
    def __init__(self):
        super().__init__(CallDetail)