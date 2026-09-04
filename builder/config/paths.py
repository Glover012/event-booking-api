from pathlib import Path

### Paths ###
# All paths that builder uses must be absolute. Each of them is currently
# resolved from the REPOSITORY_DIR, that is taken from a paths.py file location.
# CWD is skipped deliberatly to avoid problems in the future, in case
# builder can run from a different location.

# builder/config/paths.py -> builder/config -> builder -> repository
REPOSITORY_DIR = Path(__file__).resolve().parent.parent.parent

DOCKER_DIR = REPOSITORY_DIR / "docker"
ALEMBIC_VERSIONS_DIR = REPOSITORY_DIR / "alembic" / "versions"
ENV_FILE = REPOSITORY_DIR / ".env"
REVISIONS_DIR = REPOSITORY_DIR / "builder" / "revisions"
