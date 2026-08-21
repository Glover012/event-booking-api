from fastapi import APIRouter, status

from ..api.response import ApiResponse
from ..api.info import ApiInfo
from ..schemas.users import UserResponse, ChangePasswordRequest
from ..dependencies.assistants import user_assistant_dependency

### API Router ###
user_router = APIRouter(tags=["user"])


### Endpoints - minimum role USER ###
@user_router.get(
        '/me',
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
        '/me/password',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[None],
        )
def change_password(
    user_assistant: user_assistant_dependency,
    change_password_request: ChangePasswordRequest,
    ) -> ApiResponse[None]:

    user_assistant.change_password(change_password_request)

    return ApiResponse[None].success(
        ApiInfo.PASSWORD_CHANGED_SUCCESSFULLY,
        )
