from ..schemas.users import ChangePasswordRequest, UserRole
from ..services.users import UsersService
from ..core.security import PasswordHasher
from ..db.models import Users
from ..api.exceptions import HTTPError
from ..schemas.auth import MeTokenClaims


class UserAssistant:
    """
    Root of the assistant hierarchy and the helper for user level routes.

    Every account is a user, so the higher roles inherit from here.

    A higher role reaching a lower role's route is handled by the MINIMUM_ROLE check.
    """

    MINIMUM_ROLE = UserRole.USER

    def __init__(
            self,
            me_token_claims: MeTokenClaims,
            users_service: UsersService,
            ) -> None:
        self.me_token_claims = me_token_claims
        self.users_service = users_service
        self.me_model = self.verify_me()

    def verify_me(self) -> Users:
        """
        Confirms that the token data still matches a record in db and
        that its role reaches MINIMUM_ROLE.

        A missing record means the account was removed while the token
        stayed valid, so it ends as an authentication failure. An
        insufficient role ends as forbidden.
        """
        me_model = self.users_service.find_by_identity(
            id=self.me_token_claims.id,
            username=self.me_token_claims.username,
            email=self.me_token_claims.email,
        )

        if me_model is None:
            raise HTTPError.AUTHENTICATION_FAILED()

        if UserRole(me_model.role).level < self.MINIMUM_ROLE.level:
            raise HTTPError.FORBIDDEN()

        return me_model

    def get_me(self) -> Users:
        return self.me_model

    def change_me_password(
            self,
            change_password_request: ChangePasswordRequest,
            ) -> None:

        if not PasswordHasher.verify_password(
            change_password_request.old_password,
            self.me_model.hashed_password,
            ):
            raise HTTPError.INCORRECT_PASSWORD()

        if PasswordHasher.verify_password(
            change_password_request.new_password,
            self.me_model.hashed_password,
        ):
            raise HTTPError.SAME_PASSWORD()

        self.users_service.update_password(
            self.me_model,
            PasswordHasher.hash_password(
                change_password_request.new_password
            ),
        )
