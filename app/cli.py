import argparse
import logging
import sys

from .bootstrap.admin import CreateBootstrapAdmin


def create_bootstrap_admin(args: argparse.Namespace) -> None:
    CreateBootstrapAdmin().run()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m app.cli",
        description="Administrative commands for the event booking API.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_admin = subparsers.add_parser(
        "create-bootstrap-admin",
        help="Create the initial admin account when the database has none.",
    )
    create_admin.set_defaults(handler=create_bootstrap_admin)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
