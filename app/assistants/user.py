from ..schemas.users import ChangePasswordRequest, UserRole
from ..services.users import UsersService
from ..core.security import PasswordHasher
from ..db.models import Users
from ..api.exceptions import HTTPError
from ..schemas.auth import UserTokenInfo
from ..schemas.users import ChangePasswordRequest, UserRole


class UserAssistant:
    """
    Root of the assistant hierarchy and the helper for user level routes.

    Every account is a user, so the higher roles inherit from here.

    A higher role reaching a lower role's route is handled by the MINIMUM_ROLE check.
    """

    MINIMUM_ROLE = UserRole.USER

    def __init__(
            self,
            users_service: UsersService,
            user_token: UserTokenInfo,
            ) -> None:
        self.users_service = users_service
        self.user_token = user_token
        self.user_model = self.verify_user()

    def verify_user(self) -> Users:
        """
        Confirms that the token data still matches a record in db and
        that its role reaches MINIMUM_ROLE.

        A missing record means the account was removed while the token
        stayed valid, so it ends as an authentication failure. An
        insufficient role ends as forbidden.
        """
        user_model = self.users_service.find_by_identity(
            id=self.user_token.id,
            username=self.user_token.username,
            email=self.user_token.email,
        )

        if user_model is None:
            raise HTTPError.AUTHENTICATION_FAILED()

        if UserRole(user_model.role).level < self.MINIMUM_ROLE.level:
            raise HTTPError.FORBIDDEN()

        return user_model

    def get_user(self) -> Users:
        return self.user_model

    def change_password(
            self,
            change_password_request: ChangePasswordRequest,
            ) -> None:

        if not PasswordHasher.verify_password(
            change_password_request.old_password,
            self.user_model.hashed_password,
            ):
            raise HTTPError.INCORRECT_PASSWORD()

        if PasswordHasher.verify_password(
            change_password_request.new_password,
            self.user_model.hashed_password,
        ):
            raise HTTPError.SAME_PASSWORD()

        self.users_service.update_password(
            self.user_model,
            PasswordHasher.hash_password(
                change_password_request.new_password
            ),
        )
