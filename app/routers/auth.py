from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from ..core.security import create_access_token, PasswordHasher
from ..db import db_dependency
from ..db.models import Users
from ..api.response import ApiResponse
from ..api.info import ApiInfo
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
@auth_router.post("/login", response_model=ApiResponse[Token])
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
            detail=ApiResponse.fail(ApiInfo.INVALID_CREDENTIALS),
        )
    token = create_access_token(
        user_id=user.id,
        username=user.username,
        user_role=user.role,
        )

    # Only due to type checker
    token_response = Token(
        access_token = token,
        token_type = "bearer",
        )

    return ApiResponse[Token].success(
        ApiInfo.TOKEN_CREATED,
        data=token_response
        )

# Technical endpoint, only for FastAPI SwaggerUI
@auth_router.post("/test/token", response_model=Token)
def login_for_access_token_swagger(
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
            detail=ApiResponse.fail(ApiInfo.INVALID_CREDENTIALS),
        )
    token = create_access_token(
        user_id=user.id,
        username=user.username,
        user_role=user.role,
        )
    
    return {"access_token": token, "token_type": "bearer"}
