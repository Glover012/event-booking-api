from sqlalchemy.exc import IntegrityError

from ..schemas.users import RegisterUserRequest
from ..core.security import PasswordHasher
from ..schemas.users import UserRole 
from ..db.models import Users
from ..api.exceptions import HTTPError


class RegisterService:

    def __init__(self, db, service) -> None:
        self.db = db
        self.service = service

    def register_new_user(
            self,
            register_user_request: RegisterUserRequest,
            ) -> Users:

        self.service.confirm_available_credentials(
            username=register_user_request.username,
            email=register_user_request.email,
        )
        # Race condition
        try:
            # Due to resource consumption password hashing is proceeded
            # before the add/commit, when all user creation conditions are met
            new_user = Users(
                email = register_user_request.email,
                username = register_user_request.username,
                first_name = register_user_request.first_name,
                last_name = register_user_request.last_name,
                hashed_password = PasswordHasher.hash_password(
                    register_user_request.password
                    ),
                role = UserRole.USER.value,
                )
            self.db.add(new_user)
            self.db.commit()

            return new_user

        except IntegrityError:
            self.db.rollback()
            raise HTTPError.USER_ALREADY_EXISTS
