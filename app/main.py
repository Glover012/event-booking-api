from fastapi import FastAPI

from .core.config import settings
from .routers import (
    user_router, 
    auth_router, 
    health_router,
    event_router,
)
from .core.exception_handlers import register_custom_exception_handlers
from .core.logging import Logger


### Factory mode ###
def create_app(enable_file_logging: bool = True) -> FastAPI:
    ### Logging ###
    if enable_file_logging:
        Logger("app")
        Logger("access", logger_name="uvicorn.access")
        Logger("server", logger_name="uvicorn.error")

    ### App ###
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
    )

    ### Exception Handlers ###
    register_custom_exception_handlers(app)

    ### Routers ###
    app.include_router(user_router)
    app.include_router(auth_router)
    app.include_router(health_router)
    app.include_router(event_router)

    return app
