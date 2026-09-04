import argparse

from .config import (
    ALEMBIC_VERSIONS_DIR,
    CONTAINER,
    ENVIRONMENTS,
    LOCAL,
    REPOSITORY_DIR,
    Environment,
)
from .helpers import api, env_file, secrets
from .helpers.console import bold, confirm, cyan, green, red, state
from .helpers.filesystem import remove_directory
from .helpers.revisions import copy_static
from .system import (
    compose,
    run,
    running_environments,
    running_services,
    volumes,
)

### Commands ###
# Only body of the CLI commands and nothing else. Every helper is imported.

def up(args: argparse.Namespace) -> None:
    """
    Brings enviornment up, refuses when any other event-booking
    enviornment is already running.

    Writes .env since API read from it.
    """
    environment: Environment = args.environment
    active_environments = running_environments()

    if active_environments:
        for running, services in active_environments.items():
            print(f"{cyan((running.NAME).upper())} environment is up: {', '.join(services)}")

        print(bold("Run builder down first."))
        return

    if environment is LOCAL:
        env_file.write(environment)

    secrets.create(environment)

    compose(environment, "up", "-d", "--build", "--wait")

    if environment is CONTAINER:
        secrets.print_bootstrap_password(environment)
        return

    api.start_local(environment)


def down(args: argparse.Namespace) -> None:
    """
    Stops one enviornment. Nothing on disk is removed unless specific
    parameters are provided.

    The database volume and the secrets dir are always removed together, since
    the database password is stored in secret dir.

    .env isn't removed.
    """
    environment: Environment = args.environment
    remove_logs = args.logs or args.all
    remove_data = args.data or args.all

    if remove_data and not confirm(
        "This removes, permanently:",
        (
            "the database volume, with all the data",
            f"including the secrets in {environment.SECRET_DIR}",
        ),
    ):
        print("Operation aborted, nothing was removed.")
        return

    compose(environment, "down", *(["-v"] if remove_data else []))

    if remove_logs:
        remove_directory(environment, environment.LOG_DIR)

    if remove_data:
        remove_directory(environment, environment.SECRET_DIR)


def status(args: argparse.Namespace) -> None:
    """
    Print status info about every enviornment. Cover info about log and secret
    files presence, since each enviornment has them in different location.

    Directories answer without any privilege, so status never needs sudo.
    """
    active_enviornmnets = running_environments()

    print(bold(f"{'NAME':<12}{'LOGS':<12}{'SECRETS':<12}{'VOLUMES':<12}SERVICES"))

    for environment in ENVIRONMENTS:
        services = active_enviornmnets.get(environment)

        print(
            f"{cyan(f'{environment.NAME:<12}')}"
            f"{state(environment.LOG_DIR.is_dir())}"
            f"{state(environment.SECRET_DIR.is_dir())}"
            f"{state(bool(volumes(environment)))}"
            f"{', '.join(services) if services else 'None'}"
        )


def rebuild_schema(args: argparse.Namespace) -> None:
    """
    Regenerates the Alembic initial revision from the database models, 
    then re-applies the static revisions from builder/revisions.

    Runs using the local enviornment, because new revisions must be
    included in repository.

    The database must be empty, since Alembic autogenerate compares the 
    models with current db content, so a remaining volume from previous runs 
    would produce an empty migration instead of the whole inital schema.

    Nothing is left behind after a succesfull run. The result is only a set of new 
    revisions, that are verified by applying 'alembic upgrade head' and 
    'alembic down base'.
    """
    revisions = sorted(ALEMBIC_VERSIONS_DIR.glob("*.py"))
    existing = [] # Elements that will be removed/disabled

    if running_services(LOCAL):
        existing.append("the running local containers")

    if volumes(LOCAL):
        existing.append("the local database volume, with all its data")

    for directory in (LOCAL.SECRET_DIR, LOCAL.LOG_DIR):
        if directory.is_dir():
            existing.append(str(directory))

    if revisions:
        existing.append(f"{len(revisions)} revision file(s) in alembic/versions")

    if existing and not confirm("This removes, permanently:", existing):
        print("Operation aborted, nothing was removed.")
        return

    compose(LOCAL, "down", "-v")
    remove_directory(LOCAL, LOCAL.SECRET_DIR)
    remove_directory(LOCAL, LOCAL.LOG_DIR)

    for revision in revisions:
        revision.unlink()
        print(red(f"Removed {revision.relative_to(REPOSITORY_DIR)}."))

    env_file.write(LOCAL)
    secrets.create(LOCAL)

    try:
        compose(LOCAL, "up", "-d", "--wait")

        run([
            "alembic", "revision", "--autogenerate",
            "-m", "Initial database structure",
        ])

        copy_static()

        # Test both directions, upgrade and downgrade
        run(["alembic", "upgrade", "head"])
        run(["alembic", "downgrade", "base"])

    finally:
        # Removes all elements this command created, no matter the result.
        compose(LOCAL, "down", "-v")
        remove_directory(LOCAL, LOCAL.SECRET_DIR)
        remove_directory(LOCAL, LOCAL.LOG_DIR)

    print()
    for revision in sorted(ALEMBIC_VERSIONS_DIR.glob("*.py")):
        print(green(f"Created {revision.relative_to(REPOSITORY_DIR)}"))
