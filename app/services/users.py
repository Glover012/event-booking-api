from sqlalchemy import or_
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
            ) -> Users | None:
        """
        Get User model from database, based on credentials.
        If no User returns None.
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

        model = self.db.query(Users).filter(or_(*filters)).first()

        return model

    def get_model_secured(
            self,
            id: int | None = None,
            username: str | None = None,
            email: str | None = None,
            ) -> Users:
        """
        Calls get_model, but raises error when model is None. 
        Mainly due to type checker.
        """
        model = self.get_model(
            id=id,
            username=username,
            email=email,
        )
        if model is None:
            raise HTTPError.USER_DOES_NOT_EXISTS
        return model

    def confirm_available_credentials(
            self,
            username: str | None = None,
            email: str | None = None,
            ) -> bool:
        """
        Check whether user credentials are available to assign in db.
        If not raises HTTP error.
        """
        model = self.get_model(
            username=username,
            email=email,
        )
        if model:
            raise HTTPError.USER_ALREADY_EXISTS
        return True
