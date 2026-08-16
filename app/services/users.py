from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from ..db.models import Users
from ..api.exceptions import HTTPError


class UserService:
    """
    Provide ready to use db services for Users table.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_model(
            self,
            id: int | None = None,
            username: str | None = None,
            email: str | None = None,
            ) -> Users:
        """
        Load User model from database, based on credentials.
        If User is not found, raise HTTP Error.
        """

        filters = []
        if id:
            # "Users.id == id" produces SQL BinaryExpression, same as raw WHERE ...
            filters.append(Users.id == id)
        if username:
            filters.append(Users.username == username)
        if email:
            filters.append(Users.email == email)
        if not filters:
            raise ValueError("Provide at least one of: id, username, email.")

        model = self.db.query(Users).filter(and_(*filters)).first()

        if model is None:
            raise HTTPError.AUTHENTICATION_FAILED
        return model

    def find_model(
            self,
            username: str | None = None,
            email: str | None = None,
            ) -> bool:
        """
        Checks if models with provided credentials exists in db.
        Returns True, if found, else False.
        """

        filters = []
        if username:
            filters.append(Users.username == username)
        if email:
            filters.append(Users.email == email)
        if not filters:
            raise ValueError("Provide at least one of: username, email.")

        model = self.db.query(Users).filter(or_(*filters)).first()

        return model is not None

    def confirm_available_credentials(
            self,
            username: str | None = None,
            email: str | None = None,
            ) -> bool:
        """
        Checks whether provided user credentials are free to assign in db.
        If not raises HTTP error.
        """
        found = self.find_model(
            username=username,
            email=email,
        )
        if found:
            raise HTTPError.USER_ALREADY_EXISTS
        return True
