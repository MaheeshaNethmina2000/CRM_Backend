from app.util.validate_configs import validate_config_vars

validate_config_vars()

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.database_config import Base, engine
from app.config.logging_config import get_logger
from app.controller import all_routers
from app.exceptions.exception_handler import add_exception_handler

logger = get_logger(class_name=__name__)

app = FastAPI(
    description="FastAPI Service",
    version="1.0",
    title="FastAPI Service",
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(all_routers)
add_exception_handler(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
