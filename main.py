from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Absolute initialization step: Enforce validation before loading any other modules
from app.util.validate_configs import validate_startup_configurations
from app.config.database_config import engine
from app.config.logging_config import get_logger
from app.controller import all_routers
from app.exceptions.exception_handler import add_exception_handler

logger = get_logger(class_name=__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executes defensive configuration safety checks right before exposing ports to web traffic
    validate_startup_configurations()
    logger.info("Application lifespan initialization completed successfully.")
    
    yield
    
    # Cleanly disposes of all open socket pools within the async engine during container shutdown
    logger.info("Shutting down database connection engine pools...")
    await engine.dispose()
    logger.info("Lifespan context terminated cleanly.")

app = FastAPI(
    title="Sisenco Unified Operations CRM API",
    description="Enterprise core backend platform driving unified student lifecycle management pipelines",
    version="1.0.0",
    lifespan=lifespan
)

# Configures loose cross-origin access rules for front-end interface consumers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registers the global HTTP exception trapping boundaries to normalize system errors
add_exception_handler(app)

# Integrates the aggregated routing maps directly into the active application workspace
app.include_router(all_routers)

if __name__ == "__main__":
    # Boots the production ASGI server instance bounded to local host interfaces
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)