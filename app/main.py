from fastapi import FastAPI

from .core.config import settings
from .routers import user_router, auth_router, health_router
from .core.exception_handlers import register_custom_exception_handlers
from .core.logging import FileLogging


### File Logging Configuration ###
def setup_app_logging() -> None:
    FileLogging(
        app_name=settings.APP_NAME,
        log_dir=settings.LOG_DIR,
        log_level=settings.LOG_LEVEL,
        keep_files=1,
    )

### Factory mode ###
def create_app(enable_file_logging: bool = True) -> FastAPI:
    ### Logging ###
    if enable_file_logging:
        setup_app_logging()

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

    return app
