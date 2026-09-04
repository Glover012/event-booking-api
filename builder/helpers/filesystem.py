import os
import tempfile
from pathlib import Path

from ..config import Environment
from ..system import CommandFailed, run, run_root
from .console import red

### Filesystem Operations ###
# The container enviornment keeps its secrets and logs under /var, owned by
# root, while the local one keeps them inside the repository, owned by the
# current user. Therefore _run acts based on envriornment config.

def _run(
        environment: Environment,
        command: list[str],
        capture: bool = False,
        ) -> str:
    """
    Runs one command that touch a path, as whoever owns paths based on
    enviornment configuration.
    """
    if environment.NEEDS_ROOT:
        return run_root(command, capture=capture)

    return run(command, capture=capture)


def create_directory(
        environment: Environment,
        path: Path,
        mode: str = "700",
        ) -> None:
    """
    Creates the directory with its parents and sets its permissions.

    install -d does nothing when the directory is already there, so calling
    this on every up is safe and reapplies the mode.
    """
    _run(environment, ["install", "-d", "-m", mode, str(path)])


def remove_directory(environment: Environment, path: Path) -> None:
    """
    Removes a directory with everything inside it.

    The message is printed here, because both down and rebuild-schema
    destroy the same directories and would otherwise repeat it.

    A directory answers is_dir() without any privilege, so the check needs
    no sudo even under /var.
    """
    if not path.is_dir():
        print(f"Already removed: {path}.")
        return

    # -f is requried to avoid errors when dir doesn't exists
    _run(environment, ["rm", "-rf", str(path)])

    print(red(f"Removed: {path}."))


def write_secret_file(
        environment: Environment,
        path: Path,
        content: str,
        mode: str = "600",
        ) -> None:
    """
    Writes secret content into path and sets its permissions.

    The value never travels in the command line, because anyone on the
    machine can read `/proc/<pid>/cmdline`. Instead:

        1. Creates a temporary file owned by current user with 0600 
        with a random name under /tmp
        2. Writes the content into it and closes the handle, so it reaches
        disk before install reads it
        3. Copies it to the destination with the requested permissions
        4. Removes the temporary file

    Both enviornments take this path. The local one could write directly,
    but then the rule about the command line would hold in one branch only.
    """
    # Must use delete=False becase on close() it is automatically deleted
    handle = tempfile.NamedTemporaryFile("w", delete=False)

    try:
        handle.write(content)
        handle.close()

        _run(environment, ["install", "-m", mode, handle.name, str(path)])

    finally:
        os.unlink(handle.name)


def read_file(environment: Environment, path: Path) -> str:
    """Returns the file content, without the trailing newline."""
    return _run(environment, ["cat", str(path)], capture=True)


def file_exists(environment: Environment, path: Path) -> bool:
    """Answers whether one file is already present."""
    try:
        _run(environment, ["test", "-f", str(path)], capture=True)
        return True
    except CommandFailed:
        return False


def remove_file(environment: Environment, path: Path) -> None:
    """Removes one file, missing or not."""
    # -f because without it, in case file doesn't exists, error is raised
    _run(environment, ["rm", "-f", str(path)])
