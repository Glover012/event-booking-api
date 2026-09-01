import argparse

from .commands import down, status, up
from .environment import ENVIRONMENTS, Environment
from .shell import CommandFailed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m builder",
        description=(
            "Build the event booking environment, takes it down and reports "
            "what is currently running."
        ),
    )
    subparsers = parser.add_subparsers(dest="selected", required=True)

    for environment in ENVIRONMENTS:
        _add_environment(subparsers, environment)

    status_parser = subparsers.add_parser(
        "status", help="Report which environment is running."
    )
    status_parser.set_defaults(handler=status)

    return parser


def _add_environment(subparsers, environment: Environment) -> None:
    """
    Adds one enviornment branch with its up and down commands.

    The enviornment travels on the namespace instead of a flag, so the
    command names it and there is nothing to forget.
    """
    environment_parser = subparsers.add_parser(
        environment.NAME,
        help=f"Act on the {environment.NAME} environment.",
    )
    commands = environment_parser.add_subparsers(dest="command", required=True)

    up_parser = commands.add_parser(
        "up", help="Start the environment, generate secrets when missing."
    )
    up_parser.set_defaults(handler=up, environment=environment)

    down_parser = commands.add_parser(
        "down",
        help="Stop the environment. Removes nothing unless arguments provided.",
    )
    down_parser.add_argument(
        "--logs", action="store_true", help="Also remove the log directory."
    )
    down_parser.add_argument(
        "--data",
        action="store_true",
        help="Remove the database volume and the secrets. Irreversible.",
    )
    down_parser.add_argument(
        "--all", action="store_true", help="Both --logs and --data."
    )
    down_parser.set_defaults(handler=down, environment=environment)


def main() -> None:
    args = build_parser().parse_args()

    try:
        args.handler(args)
    except CommandFailed as error:
        raise SystemExit(str(error))


if __name__ == "__main__":
    main()
