import json
import shutil
from functools import cache

from .environment import ENV_FILE, Environment, ENVIRONMENTS
from .shell import run, CommandFailed


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

    --env-file absolute path is additionally provied, because compose looks for .env 
    in the directory of the compose file and all is located in docker/ dir.
    """
    env_file = ["--env-file", str(ENV_FILE)] if ENV_FILE.is_file() else []

    return run(
        [
            *compose_command(),
            *env_file,
            "-f", str(environment.COMPOSE_FILE),
            *arguments,
        ],
        capture=capture,
    )


def running_services(environment: Environment) -> list[str]:
    """
    Returns running services of one provided environment that are currently up.

    Result is scoped by the compose file, so any unrelated contrainer on the same 
    machine aren't taken into account.
    """
    output = compose(
        environment,
        "ps", "--services", "--status", "running",
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
