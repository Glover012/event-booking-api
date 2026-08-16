from sqlalchemy.orm import Session

from ..services.users import UserService
from ..schemas.users import ChangePasswordRequest, UserRole
from ..core.security import PasswordHasher
from ..db.models import Users
from ..api.exceptions import HTTPError

class BaseAssistant:
    """
    Master-class for Assistant Inheritance. Contains set of general,
    and common user related functions.
    """

    def __init__(
            self,
            db: Session,
            user_service: UserService,
            user: dict,
            minimum_role: UserRole,
            ) -> None:
        self.db = db
        self.service = user_service
        self.id = user["id"]
        self.username = user["username"]
        self.email = user["email"]
        self.role = user["role"]
        self.minimum_role = minimum_role
        self.user_model = self.verify_user(minimum_role)

    def verify_user(self, minimum_role: UserRole) -> Users:
        """
        Security function. Confirms that user data extracted 
        from JWT corresponds to record in db and
        confirms minimal required role.
        """
        user_model: Users = self.service.get_model(
            id=self.id,
            username=self.username,
            email=self.email,
        )

        if UserRole(user_model.role).level < minimum_role.level:
            raise HTTPError.FORBIDDEN

        return user_model

    def get_user(self) -> Users:
        return self.user_model

    def change_password(
            self,
            change_password_request: ChangePasswordRequest,
            ) -> None:

        if not PasswordHasher.verify_password(
            change_password_request.old_password.get_secret_value(),
            self.user_model.hashed_password,
            ):
            raise HTTPError.INCORRECT_PASSWORD

        elif PasswordHasher.verify_password(
            change_password_request.new_password.get_secret_value(),
            self.user_model.hashed_password,
            ):
            raise HTTPError.SAME_PASSWORD

        self.user_model.hashed_password = PasswordHasher.hash_password(
            change_password_request.new_password
        )
        self.db.add(self.user_model)
        self.db.commit()
