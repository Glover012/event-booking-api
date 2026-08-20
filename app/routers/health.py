from fastapi import APIRouter, status

from ..core.config import settings


### Health Router ###
health_router = APIRouter(
    prefix="/health",
    tags=["health"],
)

### Endpoints ###
@health_router.get("", status_code=status.HTTP_200_OK)
def health_check():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        }
