from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from ..core.security import decode_access_token
from ..api.info import ApiInfo
from ..api.response import ApiResponse


### Dependencies ###
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/test/token",
    auto_error=False,
    )

token_dependency = Annotated[str | None, Depends(oauth2_scheme)] # None because auto_error is False

def get_current_user(token: token_dependency):
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ApiResponse.fail(ApiInfo.NOT_AUTHENTICATED),
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(token)

        # Str to Int conversion, for SQLAlchemy queries
        user_id: int = int(payload["sub"])
        username: str = payload["username"]
        user_role: str = payload["role"]

        return {"username": username, "id": user_id, "role": user_role}

        # PyJWTError - SuperClass for all JWT exceptions
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ApiResponse.fail(ApiInfo.AUTHENTICATION_FAILED),
            headers={"WWW-Authenticate": "Bearer"},
            )
    
user_dependency = Annotated[dict, Depends(get_current_user)]
