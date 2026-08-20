from ..core.security import PasswordHasher, create_access_token
from ..db.models import Users
from ..schemas.auth import Token
from ..services.users import UsersService
from ..api.exceptions import HTTPError


class AuthAssistant:
    """
    Helper for the token endpoint.

    Outside the role hierarchy - the caller is always unauthenticated.
    """

    def __init__(self, users_service: UsersService) -> None:
        self.users_service = users_service

    def login(self, username: str, password: str) -> Token:
        """
        Exchanges credentials for an access token.
        """
        user_model = self.authenticate(username, password)

        access_token = create_access_token(
            user_id=user_model.id,
            username=user_model.username,
            email=user_model.email,
            user_role=user_model.role,
        )

        return Token(access_token=access_token, token_type="bearer")

    def authenticate(self, username: str, password: str) -> Users:
        """
        Returns the account that matches the credentials.

        A missing account and a wrong password raise the same error, so the
        response never tells the caller what exactly happened.
        """
        user_model = self.users_service.find_by_identity(username=username)

        if user_model is None or not PasswordHasher.verify_password(
            password, user_model.hashed_password
        ):
            raise HTTPError.INVALID_CREDENTIALS()

        return user_model
