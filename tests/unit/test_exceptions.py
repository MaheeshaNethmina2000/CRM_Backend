import pytest
from app.exceptions.base_exception import BaseAppException
from app.exceptions.exception import (
    BadRequestException,
    DbOperationException,
    NotFoundException,
    UnauthorizedException,
)


@pytest.mark.unit
class TestExceptions:

    def test_base_exception_defaults(self):
        exc = BaseAppException(message="error")
        assert exc.status == 500
        assert exc.message == "error"

    def test_not_found_exception(self):
        exc = NotFoundException(message="not found")
        assert exc.status == 404

    def test_bad_request_exception(self):
        exc = BadRequestException(message="bad input")
        assert exc.status == 400

    def test_unauthorized_exception(self):
        exc = UnauthorizedException(message="unauthorized")
        assert exc.status == 401

    def test_db_operation_exception(self):
        exc = DbOperationException(message="db error")
        assert exc.status == 500

    def test_exceptions_are_subclass_of_base(self):
        for exc_class in [NotFoundException, BadRequestException, UnauthorizedException, DbOperationException]:
            assert issubclass(exc_class, BaseAppException)
