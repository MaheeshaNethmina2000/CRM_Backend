class BaseAppException(Exception):
    def __init__(self, message: str, status: int = 500):
        self.message = message
        self.status = status
        super().__init__(self.message)
