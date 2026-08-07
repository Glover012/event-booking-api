from typing import Annotated

import jwt
from fastapi import Depends

from ..services.users import UserService
from ..assistants.users import UserAssistant
from ..dependencies.database import db_dependency
from ..dependencies.auth import token_dependency
from ..core.security import decode_access_token
from ..api.exceptions import HTTPError


def get_current_user(token: token_dependency):
    """
    Extract user info from JWT.
    """
    if token is None:
        raise HTTPError.NOT_AUTHENTICATED

    try:
        payload = decode_access_token(token)

        # Str to Int conversion, for SQLAlchemy queries
        user_id: int = int(payload["sub"])
        username: str = payload["username"]
        user_role: str = payload["role"]
        email: str = payload["email"]

        return {"id": user_id, "username": username, "email": email, "role": user_role}

        # PyJWTError - SuperClass for all JWT exceptions
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPError.AUTHENTICATION_FAILED

def get_user_service(db: db_dependency) -> UserService:
    return UserService(db)

def get_user_assistant(
        db: db_dependency,
        service: user_service_dependency,
        user: user_dependency,
        ) -> UserAssistant:
    return UserAssistant(db, service, user)

### Dependencies ###
user_dependency = Annotated[dict, Depends(get_current_user)] # User info from token

user_service_dependency = Annotated[UserService, Depends(get_user_service)]

user_assistant_dependency = Annotated[UserAssistant, Depends(get_user_assistant)]
