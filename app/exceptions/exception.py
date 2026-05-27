from app.exceptions.base_exception import BaseAppException


class DbOperationException(BaseAppException):
    def __init__(self, message: str, status: int = 500):
        super().__init__(message, status)


class NotFoundException(BaseAppException):
    def __init__(self, message: str, status: int = 404):
        super().__init__(message, status)


class BadRequestException(BaseAppException):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message, status)


class UnauthorizedException(BaseAppException):
    def __init__(self, message: str, status: int = 401):
        super().__init__(message, status)
