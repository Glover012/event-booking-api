from pathlib import Path

from pydantic import SecretStr


class SecretNotFound(RuntimeError):
    pass


class Secrets:

    @staticmethod
    def read_secret(name: str, secret_dir: str) -> SecretStr:
        """
        Reads a single secret from the secret_dir.
        """
        path = Path(secret_dir) / name

        if not path.is_file():
            raise SecretNotFound(f"Secret not found at {path}.")

        return SecretStr(path.read_text().strip())
