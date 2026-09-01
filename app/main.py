import logging

from fastapi import FastAPI

from .core.config import settings
from .routers import (
    health_router,
    auth_router,
    public_router,
    user_router,
    organizer_router,
    admin_router,
)
from .core.exception_handlers import register_custom_exception_handlers
from .core.logging import Logger

### Logger ###
logger = logging.getLogger(__name__)


### Factory mode ###
def create_app(enable_file_logging: bool = True) -> FastAPI:
    ### Logging ###
    if enable_file_logging:
        Logger("app")
        Logger("access", logger_name="uvicorn.access")
        Logger("server", logger_name="uvicorn.error")

        # Marks the start of a session in a log file
        logger.info(
            "Starting %s %s in %s environment.",
            settings.APP_NAME,
            settings.APP_VERSION,
            settings.ENVIRONMENT,
        )

    ### App ###
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
    )

    ### Exception Handlers ###
    register_custom_exception_handlers(app)

    ### Routers ###
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(public_router)
    app.include_router(user_router)
    app.include_router(organizer_router)
    app.include_router(admin_router)

    return app
