import logging
import os
from logging.handlers import RotatingFileHandler

from .config import settings


class Logger:
    """
    Configures logging for a single component.

    Every component writes into its own subdirectory,
    <LOG_DIR>/<component>/<component>.log, so that app, CLI,
    HTTP access and server logs never share a file and rotate
    independently.

    With logger_name left empty the root logger is set, that is 
    owned by the process and a console handler is added. With 
    logger_name given, the file handler is appended to that 
    logger, leaving its level and existing handlers untouched.
    Uvicorn logs are set to propagate=false, therefore they don't
    reach root logger and the handlers.
    """

    FORMAT = (
        f"%(asctime)s - [%(levelname)s] - {settings.APP_NAME.upper()}[%(name)s]: %(message)s"
        )
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(
            self,
            component: str,
            logger_name: str | None = None,
            ) -> None:
        self.component = component
        self.logger_name = logger_name # Root logger if None
        self.log_dir = os.path.join(settings.LOG_DIR, component)
        self.log_level_console = settings.LOG_LEVEL_CONSOLE.upper()
        self.max_bytes = settings.LOG_MAX_BYTES
        self.backup_count = settings.LOG_BACKUP_COUNT

        self.configure_logging()

    @property
    def log_file(self) -> str:
        """
        Returns full path of the active log file for current component.
        """
        return os.path.join(self.log_dir, f"{self.component}.log")

    def build_formatter(self) -> logging.Formatter:
        """
        Returns logging string formatter.
        """
        return logging.Formatter(self.FORMAT, self.DATE_FORMAT)

    def build_console_handler(self) -> logging.StreamHandler:
        """
        Console output, filtered to LOG_LEVEL_CONSOLE. These logs
        additinally reach `docker compose logs`.
        """
        handler = logging.StreamHandler()
        handler.setLevel(self.log_level_console)
        handler.setFormatter(self.build_formatter())
        return handler

    def build_file_handler(self) -> RotatingFileHandler:
        """
        File output, always at DEBUG. Rotates once the file grows past
        LOG_MAX_BYTES and keeps LOG_BACKUP_COUNT number of older copies, 
        so the directory never needs manual cleanup.
        """
        handler = RotatingFileHandler(
            self.log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding="utf-8",
        )
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(self.build_formatter())
        return handler

    def configure_logging(self) -> None:
        """
        Creates the component directory and attaches the handlers.

        The root logger is set to DEBUG so that all logs reach the 
        handles and then are filtered by their log level.
        """
        os.makedirs(self.log_dir, exist_ok=True)

        logger = logging.getLogger(self.logger_name)

        if self.logger_name is None:
            logger.setLevel(logging.DEBUG)
            logger.addHandler(self.build_console_handler())

        logger.addHandler(self.build_file_handler())
