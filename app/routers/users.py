from fastapi import APIRouter, status
from sqlalchemy.exc import IntegrityError

from ..dependencies import db_dependency, user_dependency, user_service_dependency
from ..db.models import Users
from ..core.security import PasswordHasher
from ..api.response import ApiResponse
from ..api.info import ApiInfo
from ..api.exceptions import HTTPError
from ..schemas.users import UserRole, UserResponse, RegisterUserRequest, ChangePasswordRequest

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
    user_service: user_service_dependency,
    register_user_request: RegisterUserRequest,
    ) -> ApiResponse[UserResponse]:

    user_service.confirm_available_credentials(
        username=register_user_request.username,
        email=register_user_request.email,
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
        raise HTTPError.USER_ALREADY_EXISTS

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
    user_service: user_service_dependency,
    user: user_dependency,
    ) -> ApiResponse[UserResponse]:

    user_model = user_service.get_model_secured(
        username=user["username"], 
        )

    return ApiResponse[UserResponse].success(
        ApiInfo.USER_RETRIEVED,
        data=user_model,
        )

@user_router.put(
        "/password",
        status_code=status.HTTP_200_OK, 
        response_model=ApiResponse[None],
        )
def change_password(
    db: db_dependency,
    user: user_dependency,
    user_service: user_service_dependency,
    change_password_request: ChangePasswordRequest,
    ):

    user_model = user_service.get_model_secured(
        username=user["username"], 
        )

    if not PasswordHasher.verify_password(
        change_password_request.old_password.get_secret_value(),
        user_model.hashed_password,
        ):
        raise HTTPError.INCORRECT_PASSWORD

    elif PasswordHasher.verify_password(
        change_password_request.new_password.get_secret_value(),
        user_model.hashed_password,
        ):
        raise HTTPError.SAME_PASSWORD

    user_model.hashed_password = PasswordHasher.hash_password(
        change_password_request.new_password
    )
    db.add(user_model)
    db.commit()

    return ApiResponse[None].success(
        ApiInfo.PASSWORD_CHANGED_SUCCESSFULLY
    )
