from fastapi import FastAPI

from app.core.exception_handlers import register_exception_handlers
from app.routers.files import router as files_router
from app.routers.users import router as users_router


app = FastAPI(
    title="Cloud File Storage Service",
    description="REST API for secure file upload, download, and metadata management.",
    version="0.1.0",
)

register_exception_handlers(app)

app.include_router(users_router)
app.include_router(files_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }