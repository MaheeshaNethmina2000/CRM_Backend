from app.exceptions.base_exception import BaseAppException

class DbOperationException(BaseAppException):
    def __init__(self, message: str = "Database operation failed", status_code: int = 500):
        super().__init__(message, status_code)

class NotFoundException(BaseAppException):
    def __init__(self, message: str = "The requested resource was not found", status_code: int = 404):
        super().__init__(message, status_code)

class BadRequestException(BaseAppException):
    def __init__(self, message: str = "Bad request operational parameters provided", status_code: int = 400):
        super().__init__(message, status_code)

class UnauthorizedException(BaseAppException):
    def __init__(self, message: str = "Authentication credentials are invalid or missing", status_code: int = 401):
        super().__init__(message, status_code)

class ForbiddenException(BaseAppException):
    def __init__(self, message: str = "You do not have permission to execute this operation", status_code: int = 403):
        super().__init__(message, status_code)

class InvalidStateTransitionException(BaseAppException):
    def __init__(self, message: str = "The requested lifecycle stage transition is invalid", status_code: int = 422):
        super().__init__(message, status_code)