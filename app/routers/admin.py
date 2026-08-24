from fastapi import APIRouter, status

from ..dependencies.assistants import admin_assistant_dependency
from ..api.response import ApiResponse
from ..api.info import ApiInfo
from ..schemas.users import ChangeRoleRequest, UserResponse

### API Router ###
# All admin paths share the prefix, unlike the other role routers.
admin_router = APIRouter(
    prefix="/admin", 
    tags=["admin"]
    )


### Endpoints - minimum role ADMIN ###
@admin_router.put(
        '/users/{user_id}/role',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[UserResponse],
        )
def change_user_role(
    user_id: int,
    admin_assistant: admin_assistant_dependency,
    change_role_request: ChangeRoleRequest,
    ) -> ApiResponse[UserResponse]:

    user_model = admin_assistant.change_user_role(
        user_id,
        change_role_request,
    )

    return ApiResponse[UserResponse].success(
        ApiInfo.ROLE_CHANGED,
        data=user_model,
        )
