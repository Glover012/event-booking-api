from fastapi import APIRouter, status

from ..dependencies import user_assistant_dependency, register_service_dependency
from ..api.response import ApiResponse
from ..api.info import ApiInfo
from ..schemas.users import UserResponse, RegisterUserRequest, ChangePasswordRequest

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
    register_service: register_service_dependency,
    register_user_request: RegisterUserRequest,
    ) -> ApiResponse[UserResponse]:

    new_user = register_service.register_new_user(register_user_request)

    return ApiResponse[UserResponse].success(
        ApiInfo.USER_CREATED,
        data=new_user,
        )


@user_router.get(
        "/",
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[UserResponse],
        )
def get_user_info(
    user_assistant: user_assistant_dependency,
    ) -> ApiResponse[UserResponse]:

    user_model = user_assistant.get_user()

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
    user_assistant: user_assistant_dependency,
    change_password_request: ChangePasswordRequest,
    ):

    user_assistant.change_password(change_password_request)

    return ApiResponse[None].success(
        ApiInfo.PASSWORD_CHANGED_SUCCESSFULLY
    )
