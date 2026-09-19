from ..config import SEED_FILES, Environment, variables
from ..system import compose
from .console import cyan, green


def apply(environment: Environment, dataset: str) -> None:
    """
    Streams the seed file into psql, as the database owner.

    The dataset name arrives from argparse choices and it is
    already validated.
    """
    values = variables(environment)

    print(
        f"Seeding the {cyan(environment.NAME)} database "
        f"with the {cyan(dataset)} dataset."
    )

    compose(
        environment,
        "exec",
        # TTY isn't used, since stdin is a pipe, not a terminal
        # -T instead of --no-tty, since the long form isn't present
        # in older compose versions
        "-T",
        "postgres",
        "psql",
        "--username",
        values["POSTGRES_USER"],
        "--dbname",
        values["POSTGRES_DB"],
        "--quiet",
        # psql exits with 0 even after a failure, so a broken seed
        # would look like a successful one without --set ON_ERROR_STOP=1
        "--set",
        "ON_ERROR_STOP=1",
        # BEGIN (SEED FILE CONTENT) COMMIT, single transaction, if any error
        # occurred do nothing and leave the database untouched
        "--single-transaction",
        # No -f because the file would have to exist on a container
        input=SEED_FILES[dataset].read_text(),
    )

    print(green("Seed applied."))
