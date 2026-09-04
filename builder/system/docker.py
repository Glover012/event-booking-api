import os
import shutil
from functools import cache

from ..config import ENVIRONMENTS, Environment, variables
from .shell import CommandFailed, run


@cache
def compose_command() -> list[str]:
    """
    Returns the docker compose entry cmd and writes it in cache.

    Raise when either docker or compose not found.
    """
    if shutil.which("docker"):
        try:
            run(["docker", "compose", "version"], capture=True)
            return ["docker", "compose"]
        except CommandFailed:
            raise CommandFailed("Docker compose not found.")

    raise CommandFailed("Docker not found.")


def compose(
        environment: Environment,
        *arguments: str,
        capture: bool = False,
        ) -> str:
    """
    Runs a docker compose command, along with additional arguments.
    Compose file location(-f) is hardcoded here from provided envrionment 
    configuration. 
    
    Additional docker compose arguments are simply passed.

    All required enviornment variables that docker compose needs
    are provided in run function enviornment. Therefore
    docker compose commands don't rely on .env file availability, 
    at all.
    """
    return run(
        [
            *compose_command(),
            "-f", str(environment.COMPOSE_FILE),
            *arguments,
        ],
        capture=capture,

        # os.environ returns enviornmental variables inherited by this process 
        # env= replaces the environment instead of adding to it, so
        # passing variables(environment) alone would leave the command
        # without PATH and 'docker' may not be found. Therefore contents of both 
        # have to be merged. Both objects(os._Environ and dict) are mappings, 
        # so ** can be used to unpack keys and values from them
        env={**os.environ, **variables(environment)},
    )


def running_services(environment: Environment) -> list[str]:
    """
    Returns running services of one provided environment that are currently up.

    Result is scoped by the compose file, so any unrelated contrainer on the same 
    machine aren't taken into account.
    """
    output = run(
        [
            "docker", "ps",
            "--filter", f"label=com.docker.compose.project={environment.PROJECT}",
            "--format", '{{.Label "com.docker.compose.service"}}',
        ],
        capture=True,
    )

    return output.splitlines()


def running_environments() -> dict[Environment, list[str]]:
    """
    Goes throguh every enviornment and assign its services, but only 
    when those are running. 
    
    Enviornments that don't have any service running, are left empty. Therfore
    when no enviornment have active services, result is empty dict.
    """
    return {
        environment: services
        for environment in ENVIRONMENTS
        if (services := running_services(environment))
    }

def volumes(environment: Environment) -> list[str]:
    """
    Returns the names of the volumes, or [] when none exists. Filtered by docker compose 
    project `name:`.

    Volumes survives down without `--all` or `--data` argument, so a stopped environment
    can still hold a database volume.
    """
    output = run(
        [
            "docker", "volume", "ls",
            "--filter", f"label=com.docker.compose.project={environment.PROJECT}",
            "--format", "{{.Name}}",
        ],
        capture=True,
    )

    return output.splitlines()
