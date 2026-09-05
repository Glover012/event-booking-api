import os

def start_api() -> None:
    """
    Start uvicorn and replace current process. Local only, since the container
    environment starts uvicorn from the image CMD, without --reload.
    """

    # Replaces currnet terminal process with uvicorn
    os.execvp(
        "uvicorn",
        ["uvicorn", "app.main:create_app", "--factory", "--reload"],
    )
