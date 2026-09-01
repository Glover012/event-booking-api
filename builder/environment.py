from dataclasses import dataclass
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parent.parent
ENV_FILE = REPOSITORY / ".env"


@dataclass(frozen=True, slots=True)
class Environment:
    """
    Represents a single enviornment configuration.
    """

    NAME: str
    COMPOSE_FILE: Path
    LOG_DIR: Path
    SECRET_DIR: Path
    NEEDS_ROOT: bool
    VARIABLES: tuple[tuple[str, str], ...]


# Container - runs everything in containers and keeps its secrets and logs
# under /var, therefore it requires additional root permissions for those paths
CONTAINER = Environment(
    NAME="container",
    COMPOSE_FILE=REPOSITORY / "docker" / "docker-compose.container.yaml",
    LOG_DIR=Path("/var/log/event-booking"),
    SECRET_DIR=Path("/var/lib/event-booking/secrets"),
    NEEDS_ROOT=True,
    VARIABLES=(
        ("POSTGRES_USER", "event-booking"),
        ("POSTGRES_DB", "event-booking"),
        ("POSTGRES_HOST", "postgres"),
        ("BOOTSTRAP_ADMIN_USERNAME", "master_admin"),
        ("BOOTSTRAP_ADMIN_EMAIL", "admin@example.com"),
    ),
)

# Local - runs only the Postgres container and keeps its files inside the
# repository, so it needs no root access at all
LOCAL = Environment(
    NAME="local",
    COMPOSE_FILE=REPOSITORY / "docker" / "docker-compose.local.yaml",
    LOG_DIR=REPOSITORY / "logs",
    SECRET_DIR=REPOSITORY / "secrets",
    NEEDS_ROOT=False,
    VARIABLES=(
        ("POSTGRES_USER", "event-booking"),
        ("POSTGRES_DB", "event-booking"),
        ("POSTGRES_HOST", "localhost"),
        ("BOOTSTRAP_ADMIN_USERNAME", "master_admin"),
        ("BOOTSTRAP_ADMIN_EMAIL", "admin@example.com"),
    ),
)

ENVIRONMENTS = (CONTAINER, LOCAL)
