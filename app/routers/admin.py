from fastapi import APIRouter, status

from ..dependencies.assistants import admin_assistant_dependency
from ..api.response import ApiResponse
from ..api.info import ApiInfo
from ..schemas.users import ChangeRoleRequest, UserResponseAdmin
from ..schemas.events import EventResponseOwner
from ..api.pagination import Page
from ..dependencies import pagination_dependency


### API Router ###
# All admin paths share the prefix, unlike the other role routers.
admin_router = APIRouter(
    prefix="/admin", 
    tags=["admin"]
    )


### Endpoints - minimum role ADMIN ###
@admin_router.get(
        '/users/{user_id}',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[UserResponseAdmin],
        )
def get_user(
    user_id: int,
    admin_assistant: admin_assistant_dependency,
    ) -> ApiResponse[UserResponseAdmin]:

    target_model = admin_assistant.get_user(user_id)

    return ApiResponse[UserResponseAdmin].success(
        ApiInfo.USER_RETRIEVED,
        data=target_model,
        )


@admin_router.get(
        '/users',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[Page[UserResponseAdmin]],
        )
def list_users(
    admin_assistant: admin_assistant_dependency,
    pagination: pagination_dependency,
    ) -> ApiResponse[Page[UserResponseAdmin]]:

    page = admin_assistant.list_users(pagination)

    return ApiResponse[Page[UserResponseAdmin]].success(
        ApiInfo.USERS_RETRIEVED,
        data=page,
        )


@admin_router.put(
        '/users/{user_id}/role',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[UserResponseAdmin],
        )
def change_user_role(
    user_id: int,
    admin_assistant: admin_assistant_dependency,
    change_role_request: ChangeRoleRequest,
    ) -> ApiResponse[UserResponseAdmin]:

    target_model = admin_assistant.change_user_role(
        user_id,
        change_role_request,
    )

    return ApiResponse[UserResponseAdmin].success(
        ApiInfo.ROLE_CHANGED,
        data=target_model,
        )


@admin_router.get(
        '/events/{event_id}',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[EventResponseOwner],
        )
def get_event(
    event_id: int,
    admin_assistant: admin_assistant_dependency,
    ) -> ApiResponse[EventResponseOwner]:

    event_model = admin_assistant.get_event(event_id)

    return ApiResponse[EventResponseOwner].success(
        ApiInfo.EVENT_RETRIEVED,
        data=event_model,
        )


@admin_router.get(
        '/events',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[Page[EventResponseOwner]],
        )
def list_events(
    admin_assistant: admin_assistant_dependency,
    pagination: pagination_dependency,
    ) -> ApiResponse[Page[EventResponseOwner]]:

    page = admin_assistant.list_events(pagination)

    return ApiResponse[Page[EventResponseOwner]].success(
        ApiInfo.EVENTS_RETRIEVED,
        data=page,
        )
