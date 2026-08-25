from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError

from ..schemas.auth import MeTokenClaims
from ..core.security import decode_access_token
from ..api.exceptions import HTTPError


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    auto_error=False,
    )

token_dependency = Annotated[str | None, Depends(oauth2_scheme)] # None because auto_error is False


def get_me_token_claims(token: token_dependency) -> MeTokenClaims:
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
        # model_validate constructs the pydantic model
        # from a payload dict and validates the data
        return MeTokenClaims.model_validate(payload)

    # PyJWTError - SuperClass for all JWT exceptions
    except (jwt.PyJWTError, ValidationError) as e:
        raise HTTPError.AUTHENTICATION_FAILED() from e


### Dependencies ###
me_token_claims_dependency = Annotated[
    MeTokenClaims, Depends(get_me_token_claims)
]
