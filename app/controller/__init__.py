from fastapi import APIRouter
from fastapi.responses import JSONResponse

# Central parent routing architecture for the entire CRM application
all_routers = APIRouter()

# Future feature modules will be explicitly registered below as development progresses:
# from app.controller.auth_controller import router as auth_router
# all_routers.include_router(auth_router, prefix="/auth")

@all_routers.get("/", tags=["Root"])
async def root() -> JSONResponse:
    # Provides a clean, standardized entry-point verification packet for the api framework
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Sisenco Unified Operations CRM API Gateway is running optimally"
        }
    )

@all_routers.get("/health", tags=["System Health"])
async def health() -> JSONResponse:
    # Zero-dependency diagnostic micro-endpoint used by deployment platforms to run automated health checks
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "engine": "FastAPI Asynchronous Engine 2.0"
        }
    )