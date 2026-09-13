from functools import cached_property
from urllib.parse import quote

from pydantic_settings import BaseSettings, SettingsConfigDict

from .secret_files import Secrets


class Settings(BaseSettings):
    """
    Every setting of the application, resolved once while this module is
    imported.

    The fields without a default carry no value of their own. They arrive from
    the enviornment the builder prepared - .env in the local enviornment, plain
    enviornment variables in the container one - and the values themselves live
    in builder/config/environments.py. A missing variable either from .env or
    enviornment stops the import.

    The defaults that remain describe the application itself and are the same
    in every enviornment.

    Secrets never travel through .env nor a command line. They are read from
    the files in SECRET_DIR, which the builder writes and docker compose bind
    mounts into the containers.
    """

    ### Provided by the builder enviornment configuration ###
    ENVIRONMENT: str
    ## Dirs
    SECRET_DIR: str
    LOG_DIR: str
    ## Database
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    ## Bootstrap admin
    BOOTSTRAP_ADMIN_USERNAME: str
    BOOTSTRAP_ADMIN_EMAIL: str
    BOOTSTRAP_ADMIN_FIRST_NAME: str
    BOOTSTRAP_ADMIN_LAST_NAME: str

    ### App details ###
    APP_NAME: str = "event-booking-api"
    APP_VERSION: str = "0.1.0"

    ### Database ###
    POSTGRES_PORT: int = 5432

    ### Security ###
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    ### Logging ###
    LOG_LEVEL_CONSOLE: str = "info"
    LOG_MAX_BYTES: int = 2 * 1024 * 1024
    LOG_BACKUP_COUNT: int = 10

    ### Enviornment Var Config ###
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ### Secrets ###
    def _secret(self, filename: str) -> str:
        """
        Returns one secret from SECRET_DIR. Raises SecretNotFound when that
        file is not there.
        """
        return Secrets.read_secret(filename, self.SECRET_DIR).get_secret_value()

    # Password is only read once, therefore not cached
    @property
    def BOOTSTRAP_ADMIN_PASSWORD(self) -> str:
        return self._secret("bootstrap_admin_password")

    @cached_property
    def SECRET_KEY(self) -> str:
        return self._secret("secret_key")

    @cached_property
    def POSTGRES_PASSWORD(self) -> str:
        return self._secret("postgres_password")

    ### Database connection ###
    # quote safe='' protects manually typed password which may contain
    # characters like @ or /, that alter URL structure it percent-encodes
    # them to their respective hexadecimal form like: @ -> %40
    # SQLAlchemy calls unquote while parsing URL, so it receives original
    # password
    @cached_property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:"
            f"{quote(self.POSTGRES_PASSWORD, safe='')}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
