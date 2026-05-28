from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config.logging_config import get_logger
from app.exceptions.base_exception import BaseAppException

logger = get_logger(__name__)

def add_exception_handler(app: FastAPI) -> None:
    
    @app.exception_handler(BaseAppException)
    async def base_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
        # Logs as a warning since this is a known, handled business logic rule failure
        logger.warning(f"Application exception: {exc.message} on path {request.url.path}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.__class__.__name__,
                "message": exc.message,
                "data": None
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # Logs as a critical error because this is an unhandled system crash (e.g., raw database failure)
        logger.error(f"Unhandled system exception on path {request.url.path}: {str(exc)}")
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "InternalServerError",
                "message": "An unexpected internal server error occurred.",
                "data": None
            }
        )