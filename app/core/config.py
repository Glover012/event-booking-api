from functools import cached_property
from urllib.parse import quote

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from .secret_files import Secrets


class Settings(BaseSettings):
    ### App details ###
    APP_NAME: str = "event-booking-api"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str


    ### Database credentials ###
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432


    ### Bootstrap Admin ###
    BOOTSTRAP_ADMIN_USERNAME: str | None = None
    BOOTSTRAP_ADMIN_EMAIL: str | None = None
    BOOTSTRAP_ADMIN_FIRST_NAME: str = "System"
    BOOTSTRAP_ADMIN_LAST_NAME: str = "Administrator"


    ### Security ###
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


    ### Secrets ###
    # Duplicated literally in docker-compose.yaml (bind mount) and setup.sh.
    # Changing it only here makes read_secret raise SecretNotFound.
    SECRET_DIR: str = "/var/lib/event-booking/secrets"

    # Each secret is resolved in the order: enviornment > file
    # The enviornment variable set in .env will always win.

    # DOCKER INFO
    # docker-compose don't load these secrets from .env, it only
    # takes into account the bind-mounted files, therefore
    # it is possible to use secrets in .env locally, while 
    # containers are using only the files.

    # *_ENV fields have validation_alias equal to its @cached_property
    # Code uses only @cached_properties directly. Pydantic when Settings()
    # is constructed during import, tries to load values from .env, 
    # into *_ENV variables, by their valiadation_alias. If value is absent, 
    # leaves None, so the @cached_property look for file to read.

    SECRET_KEY_ENV: SecretStr | None = Field(
        default=None, validation_alias="SECRET_KEY"
        )

    POSTGRES_PASSWORD_ENV: SecretStr | None = Field(
        default=None, validation_alias="POSTGRES_PASSWORD"
        )

    BOOTSTRAP_ADMIN_PASSWORD_ENV: SecretStr | None = Field(
        default=None, validation_alias="BOOTSTRAP_ADMIN_PASSWORD"
        )

    def _resolve(self, filename: str, env_value: SecretStr | None) -> str:
        """
        Returns a single secret, preferring the environment over the file
        in SECRET_DIR. Raises SecretNotFound when neither source provides it.
        """
        if env_value is not None:
            return env_value.get_secret_value()

        return Secrets.read_secret(filename, self.SECRET_DIR).get_secret_value()

    @cached_property
    def BOOTSTRAP_ADMIN_PASSWORD(self) -> str:
        return self._resolve(
            "bootstrap_admin_password", self.BOOTSTRAP_ADMIN_PASSWORD_ENV
            )

    @cached_property
    def SECRET_KEY(self) -> str:
        return self._resolve("secret_key", self.SECRET_KEY_ENV)

    @cached_property
    def POSTGRES_PASSWORD(self) -> str:
        return self._resolve("postgres_password", self.POSTGRES_PASSWORD_ENV)

    ### Database connection ###
    # quote safe='' protects manually typed password which may contain 
    # characters like @ or /, that alter URL structure it percent-encodes 
    # them to their respective hexadecimal form like: @ -> %40
    # SQLAlchemy calls unquote while parsing URL, so it revieve original
    # password
    @cached_property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:"
            f"{quote(self.POSTGRES_PASSWORD, safe='')}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

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
