from typing import Annotated

import jwt
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from ...core.security import token_dependency, create_access_token, PasswordHasher, decode_access_token
from ...db import db_dependency
from ...db.models import Users

### API Router ###
auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

### Validation && Models ###
class Token(BaseModel):
    access_token: str
    token_type: str

### Authentication ###
def authenticate_user(
        username: str,
        password: str,
        db: db_dependency,
        ) -> Users | None:
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return None
    if not PasswordHasher._PASSWORD_HASH.verify(
        password, str(user.hashed_password)
        ):
        return None
    return user

def get_current_user(token: token_dependency):
    try:
        payload = decode_access_token(token)

        # Str to Int conversion, for SQLAlchemy queries
        user_id: int = int(payload["sub"]) 
        username: str = payload["username"]
        user_role: str = payload["role"]

        return {"username": username, "id": user_id, "role": user_role}

        # PyJWTError - SuperClass for all JWT exceptions
    except (jwt.PyJWTError, KeyError): 
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Could not get user."
                )

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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not authenticate user."
        )
    token = create_access_token(
        user_id=user.id,
        username=user.username,
        user_role=user.role,
        )
    
    return {"access_token": token, "token_type": "bearer"}
