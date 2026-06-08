from fastapi import APIRouter
from fastapi.responses import JSONResponse

# Import all feature routers
from app.controller.staff_controller import router as staff_router
from app.controller.contact_controller import router as contact_router
# COMMENTED OUT: We will uncomment this when you actually create the ticket_controller.py file!
# from app.controller.ticket_controller import router as ticket_router
from app.controller.payment_controller import router as payment_router
from app.controller.call_center_controller import router as call_center_router
from app.controller.whatsapp_agent_controller import router as whatsapp_agent_router

# Central parent routing architecture for the entire CRM application
all_routers = APIRouter()

# Register all feature routers
all_routers.include_router(staff_router)
all_routers.include_router(contact_router)
# COMMENTED OUT:
# all_routers.include_router(ticket_router)
all_routers.include_router(payment_router)
all_routers.include_router(call_center_router)
all_routers.include_router(whatsapp_agent_router)


@all_routers.get("/", tags=["Root"])
async def root() -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Sisenco Unified Operations CRM API Gateway is running optimally"
        }
    )

@all_routers.get("/health", tags=["System Health"])
async def health() -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "engine": "FastAPI Asynchronous Engine 2.0"
        }
    )