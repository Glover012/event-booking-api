from typing import Annotated

import jwt
from fastapi import Depends
from pydantic import ValidationError

from ..services.users import UsersService
from ..assistants.user import UserAssistant
from ..schemas.auth import UserTokenInfo
from ..dependencies.database import db_dependency
from ..dependencies.auth import token_dependency
from ..core.security import decode_access_token
from ..api.exceptions import HTTPError


def get_current_user(token: token_dependency) -> UserTokenInfo:
    """
    Decodes the JWT and validates its claims.

    A malformed token, a missing claim and a claim of the 
    wrong type all end the same way - the client has to 
    authenticate again.
    """
    if token is None:
        raise HTTPError.NOT_AUTHENTICATED()

    try:
        payload = decode_access_token(token)
        # model_validate construct the pydantic model
        # from a payload dict and validate the data
        return UserTokenInfo.model_validate(payload)

    # PyJWTError - SuperClass for all JWT exceptions
    except (jwt.PyJWTError, ValidationError) as e:
        raise HTTPError.AUTHENTICATION_FAILED() from e


def get_users_service(db: db_dependency) -> UsersService:
    return UsersService(db)


def get_user_assistant(
        users_service: users_service_dependency,
        user_token: current_user_dependency,
        ) -> UserAssistant:
    return UserAssistant(users_service, user_token)


### Dependencies ###
current_user_dependency = Annotated[UserTokenInfo, Depends(get_current_user)]

users_service_dependency = Annotated[UsersService, Depends(get_users_service)]

user_assistant_dependency = Annotated[UserAssistant, Depends(get_user_assistant)]
