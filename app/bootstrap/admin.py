import logging
import os
import secrets
from pathlib import Path

from pydantic import SecretStr
from sqlalchemy.exc import IntegrityError

from ..core.config import settings
from ..core.security import PasswordHasher
from ..db.database import SessionLocal
from ..db.models import Users
from ..schemas.users import UserRole

logger = logging.getLogger(__name__)


class CreateBootstrapAdmin:
    """
    Creates the initial admin account on application boot.
    Runs only when the database contains no admin. The generated
    password is written to a file once and never logged.
    """

    def __init__(self) -> None:
        self.db = SessionLocal()

    def run(self) -> None:
        """
        Entry point for the bootstrap admin creation. Does nothing when an 
        admin already exists, and fails when no credentials were
        configured, since such an instance cannot be administered.

        The account is committed only after the password file is written,
        so that a failed write leaves no admin behind and the next boot
        retries the whole sequence.
        """

        try:
            if self.admin_exists():
                logger.info("Admin account already exists, skipping bootstrap.")
                return

            if not self.credentials_configured():
                raise SystemExit(
                    "No admin account found in the database and "
                    "BOOTSTRAP_ADMIN_USERNAME or BOOTSTRAP_ADMIN_EMAIL is not set. "
                    "Cannot bootstrap the first admin. Set missing admin credentials."
                )

            password = self.generate_password()
            self.create_admin(password) 
            self.save_password_to_file(password)
            self.db.commit() # Required due to flush in create_admin

            logger.info(
                "Admin account '%s' created. Password written to %s",
                settings.BOOTSTRAP_ADMIN_USERNAME,
                settings.BOOTSTRAP_SECRET_DIR,
            )
        finally:
            self.db.close() # Flushed/non-commited transaction is rolled

    def admin_exists(self) -> bool:
        """
        Checks whether any admin account is already present in db.
        """
        admin = (
            self.db.query(Users)
            .filter(Users.role == UserRole.ADMIN.value)
            .first()
        )
        return admin is not None

    def credentials_configured(self) -> bool:
        """
        Confirms that admin credentials were provided in .env. 
        Names are skipped, due to defaults.
        """
        return all([
            settings.BOOTSTRAP_ADMIN_USERNAME,
            settings.BOOTSTRAP_ADMIN_EMAIL,
        ])

    def generate_password(self) -> SecretStr:
        """
        Generates a random password.
        """
        return SecretStr(secrets.token_urlsafe(32))

    def create_admin(self, password: SecretStr) -> Users:
        """
        Creates the admin account. Flushes changes, so that in case of 
        errors in later steps transaction will be rolled. Raises an 
        error when the configured username or email already belongs 
        to another account.

        Requires self.db.commit() in run().
        """
        try:
            new_user = Users(
                email=settings.BOOTSTRAP_ADMIN_EMAIL,
                username=settings.BOOTSTRAP_ADMIN_USERNAME,
                first_name=settings.BOOTSTRAP_ADMIN_FIRST_NAME,
                last_name=settings.BOOTSTRAP_ADMIN_LAST_NAME,
                hashed_password=PasswordHasher.hash_password(password),
                role=UserRole.ADMIN.value,
            )
            self.db.add(new_user)
            self.db.flush()
            return new_user

        except IntegrityError:
            self.db.rollback()
            raise SystemExit(
                f"Cannot create bootstrap admin: username "
                f"'{settings.BOOTSTRAP_ADMIN_USERNAME}' or email "
                f"'{settings.BOOTSTRAP_ADMIN_EMAIL}' already belongs "
                f"to another account."
                )

    def save_password_to_file(self, password: SecretStr) -> None:
        """
        Writes the admin_password to BOOTSTRAP_SECRET_DIR with 0600, so that
        only the owner can read it.
        """
        bootstrap_dir = settings.BOOTSTRAP_SECRET_DIR
        try:
            os.makedirs(bootstrap_dir, exist_ok=True)

            flags = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
            admin_password_path = Path(bootstrap_dir) / "admin_password"
            fd = os.open(admin_password_path, flags, 0o600)

            with os.fdopen(fd, "w") as file:
                file.write(password.get_secret_value() + "\n")

        except PermissionError as e:
            raise SystemExit(f"No permissions to write {bootstrap_dir}: {e}")
        except OSError as e:
            raise SystemExit(f"File-system error writing {bootstrap_dir}: {e}")
