from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ### App details ###
    APP_NAME: str = "event-booking-api"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "local"

    ### Database connection && credentials ###
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432

    @property
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
    BOOTSTRAP_SECRET_PATH: str = "/run/bootstrap/admin_password"

    ### Security ###
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

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
