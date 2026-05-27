from fastapi import APIRouter
from starlette.responses import HTMLResponse

# Import your routers here. Example:
# from .user_controller import router as user_router

all_routers = APIRouter()

# Register your routers here. Example:
# all_routers.include_router(user_router)


@all_routers.get("/", response_class=HTMLResponse)
async def root():
    html_content = """
    <html>
        <head>
            <title>FastAPI Service</title>
        </head>
        <body>
            <h1>FastAPI Service</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@all_routers.get("/health")
async def health():
    return {"status": "ok"}
