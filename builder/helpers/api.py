import os

from ..config import Environment
from ..system import run
from . import secrets


def start_local(environment: Environment) -> None:
    """
    Local only, in the container environment uvicorn is started by the
    image CMD instead, without --reload.

    Run migration, creates bootstrap admin account. Execute and replace
    current terminal process with uvicorn.

    The password is shown before the uvicorn execution.
    """
    run(["alembic", "upgrade", "head"])
    run(["python", "-m", "app.cli", "create-bootstrap-admin"])

    secrets.print_bootstrap_password(environment)

    # Replaces currnet terminal process with uvicorn
    os.execvp(
        "uvicorn",
        ["uvicorn", "app.main:create_app", "--factory", "--reload"],
    )
