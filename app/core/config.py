from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict

from .secret_files import Secrets


class Settings(BaseSettings):
    ### App details ###
    APP_NAME: str = "event-booking-api"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "local"

    ### Database connection && credentials ###
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432

    @cached_property
    def POSTGRES_PASSWORD(self) -> str:
        return Secrets.read_secret(
            "postgres_password", self.SECRET_DIR
            ).get_secret_value()

    @cached_property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    ### Bootstrap Admin ###
    BOOTSTRAP_ADMIN_USERNAME: str | None = None
    BOOTSTRAP_ADMIN_EMAIL: str | None = None
    BOOTSTRAP_ADMIN_FIRST_NAME: str = "System"
    BOOTSTRAP_ADMIN_LAST_NAME: str = "Administrator"
    # Duplicated literally as the volume target in docker-compose.yaml.
    BOOTSTRAP_SECRET_DIR: str = "/var/lib/event-booking/bootstrap"

    ### Security ###
    # Duplicated literally in docker-compose.yaml (bind mount) and setup.sh.
    # Changing it only here makes read_secret raise SecretNotFound.
    SECRET_DIR: str = "/var/lib/event-booking/secrets"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @cached_property
    def SECRET_KEY(self) -> str:
        return Secrets.read_secret(
            "secret_key", self.SECRET_DIR
            ).get_secret_value()

    ### Logging ###
    LOG_DIR: str = "/var/log/event-booking"
    LOG_LEVEL_CONSOLE: str = "info"
    LOG_MAX_BYTES: int = 2 * 1024 * 1024
    LOG_BACKUP_COUNT: int = 10

    ### Enviornment Var Config ###
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
