import os
import secrets
import tempfile
from pathlib import Path

from .environment import Environment
from .shell import CommandFailed, run_root

SECRET_NAMES = ("secret_key", "postgres_password", "bootstrap_admin_password")
BOOTSTRAP_PASSWORD = "bootstrap_admin_password"


def create(environment: Environment) -> None:
    """
    Creates the secret directory and any missing secret inside it.

    Existing secrets are never overwritten, since POSTGRES_PASSWORD only 
    reaches Postgres while being initialised, so a new one would not match 
    a volume that already exists.
    """
    _create_directory(environment)

    for name in SECRET_NAMES:
        if exists(environment, name):
            print(f"{name} already exists and will be used.")
            continue

        _write(environment, name, secrets.token_hex(32))


def path(environment: Environment, name: str) -> Path:
    """Returns secret path."""
    return environment.SECRET_DIR / name


def exists(environment: Environment, name: str) -> bool:
    """
    Answers whether one secret file is already present.

    The container enviornment secret dir is 700 and owned by root, so
    commands must go throught sudo.

    The local enviornment writes into user owned secret dir and is read 
    directly.
    """
    if not environment.NEEDS_ROOT:
        return path(environment, name).is_file()

    try:
        run_root(["test", "-f", str(path(environment, name))], capture=True)
        return True
    except CommandFailed:
        return False


def read(environment: Environment, name: str) -> str:
    if not environment.NEEDS_ROOT:
        return path(environment, name).read_text().strip()

    return run_root(["cat", str(path(environment, name))], capture=True)


def remove(environment: Environment, name: str) -> None:
    """Remove secret file."""
    if not environment.NEEDS_ROOT:
        path(environment, name).unlink(missing_ok=True)
        return

    # -f because without it, in case file doesn't exists, error is raised
    run_root(["rm", "-f", str(path(environment, name))])


### Helpers ###
def _create_directory(environment: Environment) -> None:
    if not environment.NEEDS_ROOT:
        environment.SECRET_DIR.mkdir(parents=True, exist_ok=True)
        os.chmod(environment.SECRET_DIR, 0o700)
        return

    run_root(["install", "-d", "-m", "700", str(environment.SECRET_DIR)])


def _write(environment: Environment, name: str, value: str) -> None:
    """
    Writes a provided secret value to a `name` file into secret path.

    The container enviornment:
        Uses a temporary file to write and store secret value and remove it 
        immediately when function is done. Command line isn't used because
        secret value may be exposed by reading `/proc/<pid>/cmdline` by anyone
        using machine.

        1. Creates a temporary file with a random name under /tmp
        2. Writes the secret value into it and closes the handle, so the
        content reaches disk before install reads it
        3. Copies it to the destination under `name` as root, setting the 
        600 privileges
        4. Removes the temporary file

    The local enviornment writes directly into repo dir and the file 
    belongs to the current user.
    """
    destination = path(environment, name)

    if not environment.NEEDS_ROOT:
        destination.write_text(f"{value}\n")
        os.chmod(destination, 0o600)
        return

    # Must use delete=Flase becase on close() it is automatically deleted
    handle = tempfile.NamedTemporaryFile("w", delete=False)

    try:
        handle.write(f"{value}\n")
        handle.close()

        run_root(["install", "-m", "600", handle.name, str(destination)])

    finally:
        os.unlink(handle.name)
