from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db.models import Users
from ..api.exceptions import HTTPError
from ..core.security import HashedPassword

class UsersService:
    """
    Provide ready to use db services for the Users table.
    """

    def __init__(self, db: Session):
        self.db = db

    def find_by_identity(
            self,
            id: int | None = None,
            username: str | None = None,
            email: str | None = None,
            ) -> Users | None:
        """
        Returns the account model that matches all provided credentials, 
        or None.

        Does not raise the error. The decision is left for the assistant.
        """
        filters = []
        if id:
            filters.append(Users.id == id)
        if username:
            filters.append(Users.username == username)
        if email:
            filters.append(Users.email == email)
        if not filters:
            raise ValueError("Provide at least one of: id, username, email.")

        return self.db.query(Users).filter(and_(*filters)).first()

    def credentials_taken(
            self,
            username: str | None = None,
            email: str | None = None,
            ) -> bool:
        """
        Checks whether any account already uses the username or the email.
        """
        filters = []
        if username:
            filters.append(Users.username == username)
        if email:
            filters.append(Users.email == email)
        if not filters:
            raise ValueError("Provide at least one of: username, email.")

        return self.db.query(Users).filter(or_(*filters)).first() is not None

    def create(
            self,
            username: str,
            email: str,
            first_name: str,
            last_name: str,
            hashed_password: HashedPassword,
            role: str,
            ) -> Users:
        """
        Creates a new User account. The provided password has to be already 
        hashed, therefore the plaintext never reaches this layer.

        The unique constraints on email and username are what finally
        prevent a duplicate.
        """

        try:
            new_user = Users(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                hashed_password=hashed_password,
                role=role
            )
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)

            return new_user

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPError.USER_ALREADY_EXISTS() from e

    def update_password(
            self,
            user_model: Users,
            hashed_password: HashedPassword,
            ) -> None:
        """
        Updates the password on an existing account
        """
        try:
            user_model.hashed_password = hashed_password
            self.db.add(user_model)
            self.db.commit()

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPError.TRANSACTION_REFUSED() from e
