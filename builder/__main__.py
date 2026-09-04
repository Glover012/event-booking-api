import argparse

from .commands import down, rebuild_schema, status, up
from .config import ENVIRONMENTS, Environment
from .system import CommandFailed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m builder",
        description=(
            "Build the event booking environment, takes it down and print status. "
        ),
    )
    subparsers = parser.add_subparsers(dest="selected", required=True)

    for environment in ENVIRONMENTS:
        _add_environment(subparsers, environment)

    status_parser = subparsers.add_parser(
        "status",
        help=(
            "Print status info about every enviornment. Cover info about log and secret"
            " files presence, since each enviornment has them in different location."
            )
        )
    status_parser.set_defaults(handler=status)

    schema_parser = subparsers.add_parser(
        "rebuild-schema",
        help=(
            "Regenerate the initial Alembic revision from the database models and re-apply the "
            "static revisions from builder/revisions. Furthermore it test generated and applied static "
            "revisions by applying 'alembic upgrade head' and 'alembic down base', on empty postgres "
            "container. It uses the local environment, therefore any remaining elements of previous local "
            "instance will be purged."
        ),
    )
    schema_parser.set_defaults(handler=rebuild_schema)

    return parser


def _add_environment(subparsers, environment: Environment) -> None:
    """
    Adds one enviornment with its up and down commands.
    """
    environment_parser = subparsers.add_parser(
        environment.NAME,
        help=f"Act on the {(environment.NAME).upper()} environment.",
    )
    commands = environment_parser.add_subparsers(dest="command", required=True)

    up_parser = commands.add_parser(
        "up",
        help=(
            "Start the environment, generate secrets when missing."
            "If secrets or volumes already exists, reuse them."
        )
    )
    up_parser.set_defaults(handler=up, environment=environment)

    down_parser = commands.add_parser(
        "down",
        help="Stop the environment. Nothing is removed, unless arguments provided.",
    )
    down_parser.add_argument(
        "--logs", action="store_true", help="Remove the log directory. Irreversible."
    )
    down_parser.add_argument(
        "--data",
        action="store_true",
        help="Remove the database volume and the secrets. Irreversible.",
    )
    down_parser.add_argument(
        "--all", action="store_true", help="Remove both --logs and --data."
    )
    down_parser.set_defaults(handler=down, environment=environment)


def main() -> None:
    args = build_parser().parse_args()

    try:
        args.handler(args)

    # CommandFailed carries the whole command error info
    except CommandFailed as error:
        raise SystemExit(str(error))

    except KeyboardInterrupt:
        raise SystemExit("Aborted.")

if __name__ == "__main__":
    main()
