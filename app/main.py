from fastapi import FastAPI, status

from .core import settings
from .api import user_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    )

@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        }

### Routers ###
app.include_router(user_router)
