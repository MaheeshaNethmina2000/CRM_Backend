from fastapi import APIRouter
from fastapi.responses import JSONResponse

# Import all feature routers
from app.controller.staff_controller import router as staff_router
from app.controller.contact_controller import router as contact_router
from app.controller.ticket_controller import router as ticket_router
from app.controller.payment_controller import router as payment_router
from app.controller.call_detail_controller import router as call_detail_router
from app.controller.whatsapp_agent_controller import router as whatsapp_agent_router
# Central parent routing architecture for the entire CRM application
all_routers = APIRouter()

# Register all feature routers
all_routers.include_router(staff_router)
all_routers.include_router(contact_router)
all_routers.include_router(ticket_router)
all_routers.include_router(payment_router)
all_routers.include_router(call_detail_router)
all_routers.include_router(whatsapp_agent_router)
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