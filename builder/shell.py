import subprocess


### Shell commands ###
# This file contains a set of functions which are responsible for 
# streaming commands directly into the terminal.
#  run - run command as current user
# run_root - run command as root user, (attaches sudo to run function)

class CommandFailed(RuntimeError):
    pass


def run(command: list[str], capture: bool = False) -> str:
    """
    Runs a command as the current user.

    Output is streaming to the terminal, unless capture is True.
    """
    result = subprocess.run(command, text=True, capture_output=capture)

    if result.returncode != 0:
        raise CommandFailed(
            f"{' '.join(command)} exited with {result.returncode}"
        )

    return (result.stdout or "").strip()


def run_root(command: list[str], capture: bool = False) -> str:
    """
    Runs one command with sudo permissions.

    Reserved for path operations under /var. Everything else stays under the
    current user.
    """
    return run(["sudo", *command], capture=capture)
