from typing import Annotated
from pydantic import SecretStr

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from ..schemas.auth import Token
from ..dependencies import auth_assistant_dependency

### API Router ###
auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


### Endpoints ###
@auth_router.post(
        '/token',
        response_model=Token,
        )
def login_for_access_token(
    auth_assistant: auth_assistant_dependency,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    ) -> Token:

    return auth_assistant.login(
        form_data.username, 
        SecretStr(form_data.password)
        )
