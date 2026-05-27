from fastapi import Request
from fastapi.responses import JSONResponse

from app.config.logging_config import get_logger
from app.exceptions.base_exception import BaseAppException
from app.model.generic_response import GenericResponse

logger = get_logger(__name__)


def add_exception_handler(app):
    @app.exception_handler(BaseAppException)
    async def base_exception_handler(request: Request, exc: BaseAppException):
        logger.error(f"Exception occurred: {exc.message}")
        response = GenericResponse.failed(
            message=exc.message,
            status_code=exc.status,
            results=[],
        )
        return JSONResponse(status_code=exc.status, content=response.to_dict())

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}")
        response = GenericResponse.failed(
            message="Internal server error",
            status_code=500,
            results=[],
        )
        return JSONResponse(status_code=500, content=response.to_dict())
