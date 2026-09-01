import argparse
import os
from pathlib import Path

from . import env_file, secrets
from .shell import run, run_root
from .docker import compose, running_environments
from .environment import CONTAINER, ENV_FILE, Environment, ENVIRONMENTS


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
            print(f"{running.NAME} environment is up: {', '.join(services)}")

        print("Run builder down first.")
        return

    env_file.write(environment)
    secrets.create(environment)

    compose(environment, "up", "-d", "--build", "--wait")

    if environment is CONTAINER:
        _print_bootstrap_password(environment)
        return

    _start_api(environment)


def down(args: argparse.Namespace) -> None:
    """
    Stops one enviornment. Nothing on disk is removed unless specific
    parameters are provided.

    The database volume and the secrets dir are always removed together, since
    the database password is stored in secret dir.

    .env isn't removed.
    """
    environment = args.environment
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
    Returns status info about every enviornment. Cover info about log and secret
    files presence, since each enviornment has them in different location.

    Directories answer without any privilege, so status never needs sudo.
    """
    active_enviornmnets = running_environments()

    print(f"{'NAME':<12}{'LOGS':<12}{'SECRETS':<12}SERVICES")

    for environment in ENVIRONMENTS:
        services = active_enviornmnets.get(environment)

        print(
            f"{environment.NAME:<12}"
            f"{_state(environment.LOG_DIR):<12}"
            f"{_state(environment.SECRET_DIR):<12}"
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

    print(f"\nBootstrap admin password: {password}")
    print("Copy and change it after the first login.")

    if input("Remove the password? [y/N] ").strip().lower() == "y":
        secrets.remove(environment, secrets.BOOTSTRAP_PASSWORD)
        print("bootstrap_admin_password removed.")


def _start_api(environment: Environment) -> None:
    """
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
    print("This removes, permanently:")
    print("  - the database volume, with all the data")
    print(f"  - including the secrets in {environment.SECRET_DIR}")

    return input("Continue? [y/N] ").strip().lower() == "y"


def _remove_directory(environment: Environment, path) -> None:
    # -f is requried to avoid errors when dir doesn't exists
    if not path.is_dir():
        return

    if environment.NEEDS_ROOT:
        run_root(["rm", "-rf", str(path)])
    else:
        run(["rm", "-rf", str(path)])

    print(f"Removed {path}.")


def _state(path: Path) -> str:
    """Simple check whether dir exists."""
    return "present" if path.is_dir() else "None"
