from fastapi import FastAPI, status

from .core.config import settings
from .routers import user_router, auth_router
from .core.exception_handlers import register_custom_exception_handlers

### App ###
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    )

register_custom_exception_handlers(app)

### Endpoints ###
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        }

### Routers ###
app.include_router(user_router)
app.include_router(auth_router)
