from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from ..db import db_dependency
from ..db.models import Users
from ..core.security import PasswordHasher
from ..api.response import ApiResponse
from ..api.info import ApiInfo
from ..schemas.users import UserRole, UserResponse, RegisterUserRequest
from ..dependencies.auth import user_dependency

### API Router ###
user_router = APIRouter(
    prefix="/user",
    tags=["user"]
)

### Endpoints ###
@user_router.post(
        '/', 
        status_code=status.HTTP_201_CREATED,
        response_model=ApiResponse[UserResponse]
        )
def register_user(
    db: db_dependency,
    register_user_request: RegisterUserRequest
    ) -> ApiResponse[UserResponse]:
    user_exists = db.query(Users).filter(
        or_(
            Users.username == register_user_request.username,
            Users.email == register_user_request.email,
            )
            ).first()

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ApiResponse.fail(ApiInfo.USER_ALREADY_EXISTS),
        )

    # Race condition
    try:
        # Due to resource consumption password hashing is proceeded
        # before the add/commit, when all user creation conditions are met
        new_user = Users(
            email = register_user_request.email,
            username = register_user_request.username,
            first_name = register_user_request.first_name,
            last_name = register_user_request.last_name,
            hashed_password = PasswordHasher.hash_password(
                register_user_request.password
                ),
            role = UserRole.USER.value,
            )
        db.add(new_user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ApiResponse.fail(ApiInfo.USER_ALREADY_EXISTS),
        )

    return ApiResponse[UserResponse].success(
        ApiInfo.USER_CREATED,
        data=new_user,
        )


@user_router.get(
        "/",
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[UserResponse],
        )
def get_user(
    db: db_dependency,
    user: user_dependency,
    ) -> ApiResponse[UserResponse]:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=ApiResponse.fail(ApiInfo.AUTHENTICATION_FAILED)
            )
    user_model = db.query(Users).filter(Users.username == user["username"]).first()
    return ApiResponse[UserResponse].success(
        ApiInfo.USER_RETRIEVED,
        data=user_model,
        )
