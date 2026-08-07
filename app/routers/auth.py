from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from ..dependencies import db_dependency
from ..core.security import create_access_token, PasswordHasher
from ..db.models import Users
from ..api.exceptions import HTTPError
from ..schemas.auth import Token


### API Router ###
auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

### Authentication ###
def authenticate_user(
        username: str,
        password: str,
        db: db_dependency,
        ) -> Users | None:
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return None
    if not PasswordHasher.verify_password(
        password, str(user.hashed_password)
        ):
        return None
    return user

### Endpoints ###
@auth_router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
    ):
    user = authenticate_user(
        form_data.username,
        form_data.password,
        db,
        )
    if user is None:
        raise HTTPError.INVALID_CREDENTIALS

    token = create_access_token(
        user_id=user.id,
        username=user.username,
        email=user.email,
        user_role=user.role,
        )
    
    return {"access_token": token, "token_type": "bearer"}
