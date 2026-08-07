from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer


### Dependencies ###
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    auto_error=False,
    )

token_dependency = Annotated[str | None, Depends(oauth2_scheme)] # None because auto_error is False
