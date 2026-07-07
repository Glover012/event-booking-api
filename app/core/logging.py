import logging
import os
from datetime import datetime


logger = logging.getLogger(__name__)


class FileLogging:
    """Configures file logging."""
    log_dir: str
    log_level: str
    app_name: str
    keep_files: int

    def __init__(
            self, 
            app_name: str, 
            log_dir: str, 
            log_level: str, 
            keep_files: int
        ) -> None:
        self.app_name = app_name
        self.log_dir = log_dir
        self.log_level = log_level.upper()
        self.keep_files = int(keep_files)
        self.configure_logging()
        self.cleanup_old_log_files(self.keep_files)

    def cleanup_old_log_files(self, keep: int = 1) -> None:
        """Remove old log files."""
        log_files = []

        for file_name in os.listdir(self.log_dir):
            file_path = os.path.join(self.log_dir, file_name)
            if (
                os.path.isfile(file_path)
                and file_name.startswith(f"{self.app_name}")
                and ".log" in file_name
            ):
                log_files.append(file_path)

        # Sort files in log_files by modification time
        log_files.sort(key=os.path.getmtime, reverse=True)

        for old_log_file in log_files[keep:]:
            try:
                os.remove(old_log_file)
                logger.info("Removed old log file: %s.", old_log_file)
            except OSError as error:
                logger.warning("Could not remove old log file %s. Error: %s", old_log_file, error)

    def configure_logging(self) -> None:
        """
        Configure console and file logging. Log file is set to DEBUG level.
        """
        console_log_level = getattr(logging, self.log_level, logging.DEBUG)

        # If dir exist don't raise error - exist_ok=True
        os.makedirs(self.log_dir, exist_ok=True)

        session_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        log_file = os.path.join(self.log_dir, f"{self.app_name}-{session_timestamp}.log")

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )

        # StreamHanlder send logs to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_log_level)
        console_handler.setFormatter(formatter)

        file_handler = logging.FileHandler(
            log_file,
            mode="w",
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Logs are sent to console and saved in logs dir
        logging.basicConfig(
            level=self.log_level,
            handlers=[console_handler, file_handler],
            force=True,
        )

        logger.debug("Logging configured. Session log file: %s", os.path.abspath(log_file))
