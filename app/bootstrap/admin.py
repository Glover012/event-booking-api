import logging

from pydantic import SecretStr
from sqlalchemy.exc import IntegrityError

from ..core.config import settings
from ..core.secret_files import SecretNotFound
from ..core.security import PasswordHasher
from ..db.database import SessionLocal
from ..db.models import Users
from ..schemas.users import UserRole

logger = logging.getLogger(__name__)


class CreateBootstrapAdmin:
    """
    Creates the initial admin account on application boot.
    Runs only when the database contains no admin. The password may
    be read from a file or enviornment variable. For deployment, file
    solution must be taken. Enviornment variable in .env have priority and can
    be used only for CI/CD and local development.

        Password read priorty: enviornment > file

    > After succesfull deployment, password_file must be removed from
    a host machine.
    """

    def __init__(self) -> None:
        self.db = SessionLocal()

    def run(self) -> None:
        """
        Entry point for the bootstrap admin creation. Does nothing when an
        admin already exists, and fails when no credentials were
        configured, since such an instance cannot be administered.
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

            password = self.read_password()
            self.create_admin(password)
            self.db.commit() # Required due to flush in create_admin

            logger.info(
                "Admin account '%s' created.",
                settings.BOOTSTRAP_ADMIN_USERNAME,
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
        Names are skipped, due to defaults. The password is checked
        separately, since it has its own two sources.
        """
        return all([
            settings.BOOTSTRAP_ADMIN_USERNAME,
            settings.BOOTSTRAP_ADMIN_EMAIL,
        ])

    def read_password(self) -> SecretStr:
        """
        Reads the password from the environment or SECRET_DIR.

        Executed only when the database has no admin present.
        """
        try:
            return SecretStr(settings.BOOTSTRAP_ADMIN_PASSWORD)
        except SecretNotFound as e:
            raise SystemExit(
                f"No admin account found in the database and no bootstrap "
                f"password available ({e}). Set BOOTSTRAP_ADMIN_PASSWORD or "
                f"run setup.sh to generate the secret file."
            )

    def create_admin(self, password: SecretStr) -> Users:
        """
        Creates the admin account. Flushes changes, so that in case of
        errors in later steps, transaction will be rolled. Raises an
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
