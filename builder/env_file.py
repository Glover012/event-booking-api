from .environment import ENV_FILE, Environment

HEADER = (
    "# Written by python -m builder up.",
    "# Manual edits will be overwritten on the next run "
    "# - variable values are located in: builder/environment.py.",
)


def write(environment: Environment) -> None:
    """
    Writes .env for the selected enviornment.

    Both compose and API(through pydantic-settings) reads from .env file.

    Two enviornments cannot run at once, because both use same port 8000.

    Secrets are located in designated enviornment SECRET_DIR as files and a
    regenerated .env file never replaces them. Therefore it is possible
    to easly switch between enviornments without losing anything.
    """
    lines = [
        *HEADER,
        "",
        f"ENVIRONMENT={environment.NAME}",
        f"SECRET_DIR={environment.SECRET_DIR}",
        f"LOG_DIR={environment.LOG_DIR}",
        "",
        *(f"{key}={value}" for key, value in environment.VARIABLES),
    ]

    ENV_FILE.write_text("\n".join(lines) + "\n")
