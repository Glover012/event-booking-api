import argparse
import os
from pathlib import Path

from . import env_file, secrets
from .output import bold, cyan, green, red, yellow
from .shell import run, run_root
from .docker import compose, running_environments, volumes
from .environment import CONTAINER, Environment, ENVIRONMENTS, LOCAL


def up(args: argparse.Namespace) -> None:
    """
    Brings enviornment up, refuses when any other event-booking
    enviornment is already running.

    Writes .env before anything else, since compose and API read
    from it.
    """
    environment = args.environment
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
        _print_bootstrap_password(environment)
        return

    _start_local_api(environment)


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

    if remove_data and not _confirmed(environment):
        print("Operation aborted, nothing was removed.")
        return

    compose(environment, "down", *(["-v"] if remove_data else []))

    if remove_logs:
        _remove_directory(environment, environment.LOG_DIR)

    if remove_data:
        _remove_directory(environment, environment.SECRET_DIR)


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
            f"{_state(environment.LOG_DIR.is_dir())}"
            f"{_state(environment.SECRET_DIR.is_dir())}"
            f"{_state(bool(volumes(environment)))}"
            f"{', '.join(services) if services else 'None'}"
        )

### Helpers ###
def _print_bootstrap_password(environment: Environment) -> None:
    """
    Print the bootstrap admin password once and offers to delete the file.

    Only bootstrap admin password is disposable. Other secrets are required
    for the next runs with the same db volume.
    """
    if not secrets.exists(environment, secrets.BOOTSTRAP_PASSWORD):
        print("Bootstrap admin password already removed.")
        return

    password = secrets.read(environment, secrets.BOOTSTRAP_PASSWORD)

    print(f"\nBootstrap admin password: {bold(yellow(password))}")
    print(bold("Copy and change it after the first login."))

    if input("Remove the password? [y/N] ").strip().lower() == "y":
        secrets.remove(environment, secrets.BOOTSTRAP_PASSWORD)
        print(red("bootstrap_admin_password removed."))


def _start_local_api(environment: Environment) -> None:
    """
    Local only, in the container environment uvicorn is started by the
    image CMD instead, without --reload.

    Run migration, creates bootstrap admin account. Execute and replace
    current terminal process with uvicorn.

    The password is shown before the uvicorn execution.
    """
    run(["alembic", "upgrade", "head"])
    run(["python", "-m", "app.cli", "create-bootstrap-admin"])

    _print_bootstrap_password(environment)

    # Replaces currnet terminal process with uvicorn
    os.execvp(
        "uvicorn",
        ["uvicorn", "app.main:create_app", "--factory", "--reload"],
    )


def _confirmed(environment: Environment) -> bool:
    """
    Confirmation popup with info regarding deletion.
    """
    print(red("This removes, permanently:"))
    print("  - the database volume, with all the data")
    print(f"  - including the secrets in {environment.SECRET_DIR}")

    return input("Continue? [y/N] ").strip().lower() == "y"


def _remove_directory(environment: Environment, path: Path) -> None:
    if not path.is_dir():
        print(f"Already removed: {path}.")
        return

    # -f is requried to avoid errors when dir doesn't exists
    if environment.NEEDS_ROOT:
        run_root(["rm", "-rf", str(path)])
    else:
        run(["rm", "-rf", str(path)])

    print(red(f"Removed: {path}."))


def _state(present: bool) -> str:
    """
    Returns info based on dir/volume presence. If true color it green.
    """
    # Add padding before colouring, since ANSI codes are invisible but
    # still counted, therefroe padding a coloured string would misalign
    # every row below the header.
    return green(f"{'True':<12}") if present else f"{'None':<12}"
