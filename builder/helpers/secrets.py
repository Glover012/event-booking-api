import secrets
from pathlib import Path

from ..config import Environment, SECRET_NAMES, BOOTSTRAP_PASSWORD
from . import filesystem
from .console import bold, green, red, yellow


def create(environment: Environment) -> None:
    """
    Creates the secret directory and any missing secret inside it.

    Existing secrets are never overwritten, since POSTGRES_PASSWORD only 
    reaches Postgres while being initialised, so a new one would not match 
    a volume that already exists.
    """
    filesystem.create_directory(environment, environment.SECRET_DIR)

    for name in SECRET_NAMES:
        if exists(environment, name):
            print(f"{green(name)} already exists and will be used.")
            continue

        filesystem.write_secret_file(
            environment,
            path(environment, name),
            f"{secrets.token_hex(32)}\n",
        )


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
    return filesystem.file_exists(environment, path(environment, name))


def read(environment: Environment, name: str) -> str:
    return filesystem.read_file(environment, path(environment, name))


def remove(environment: Environment, name: str) -> None:
    """Remove secret file."""
    filesystem.remove_file(environment, path(environment, name))


def print_bootstrap_password(environment: Environment) -> None:
    """
    Print the bootstrap admin password once and offers to delete the file.

    Only bootstrap admin password is disposable. Other secrets are required
    for the next runs with the same db volume.
    """
    if not exists(environment, BOOTSTRAP_PASSWORD):
        print("Bootstrap admin password already removed.")
        return

    password = read(environment, BOOTSTRAP_PASSWORD)

    print(f"\nBootstrap admin password: {bold(yellow(password))}")
    print(bold("Copy and change it after the first login."))

    try:
        if input("Remove the password? [y/N] ").strip().lower() == "y":
            remove(environment, BOOTSTRAP_PASSWORD)
            print(red("bootstrap_admin_password removed."))
    except EOFError: # No action is performed - in case Ctrl+D or GitHub Actions < /dev/null
        return
