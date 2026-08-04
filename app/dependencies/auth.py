from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from ..core.security import decode_access_token
from ..api.exceptions import HTTPError


### Dependencies ###
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    auto_error=False,
    )

token_dependency = Annotated[str | None, Depends(oauth2_scheme)] # None because auto_error is False

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

        return {"username": username, "id": user_id, "role": user_role}

        # PyJWTError - SuperClass for all JWT exceptions
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPError.AUTHENTICATION_FAILED
