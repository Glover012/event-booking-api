from ..config import ENV_FILE, Environment, variables

HEADER = (
    "# Written by python -m builder up/rebuild-schema.",
    "# Manual edits will be overwritten on the next run ",
    "# - variable values are located in: builder/config/environments.py.",
)


def write(environment: Environment) -> None:
    """
    Writes .env for the selected enviornment.

    API(through pydantic-settings) reads from .env file.

    Two enviornments cannot run at once, because both use same port 8000.

    Secrets are located in designated enviornment SECRET_DIR as files and a
    regenerated .env file never replaces them. Therefore it is possible
    to easly switch between enviornments without losing anything.
    """
    lines = [
        *HEADER,
        "",
        *(f"{key}={value}" for key, value in variables(environment).items()),
    ]

    ENV_FILE.write_text("\n".join(lines) + "\n")
