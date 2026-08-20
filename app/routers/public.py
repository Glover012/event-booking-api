from fastapi import APIRouter, status

from ..dependencies import public_assistant_dependency, pagination_dependency
from ..api.response import ApiResponse
from ..api.pagination import Page
from ..api.info import ApiInfo
from ..schemas.events import EventResponse
from ..schemas.users import UserResponse, RegisterUserRequest

### API Router ###
# No prefix: this router serves more than one resource, so full paths
# are declared per endpoint.
public_router = APIRouter(tags=["public"])


### Endpoints - no authentication ###
@public_router.post(
        '/users',
        status_code=status.HTTP_201_CREATED,
        response_model=ApiResponse[UserResponse],
        )
def register_user(
    public_assistant: public_assistant_dependency,
    register_user_request: RegisterUserRequest,
    ) -> ApiResponse[UserResponse]:

    new_user = public_assistant.register_user(register_user_request)

    return ApiResponse[UserResponse].success(
        ApiInfo.USER_CREATED,
        data=new_user,
        )


@public_router.get(
        '/events',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[Page[EventResponse]],
        )
def list_events(
    public_assistant: public_assistant_dependency,
    pagination: pagination_dependency,
    ) -> ApiResponse[Page[EventResponse]]:

    page = public_assistant.list_events(pagination)

    return ApiResponse[Page[EventResponse]].success(
        ApiInfo.EVENTS_RETRIEVED,
        data=page,
        )


@public_router.get(
        '/events/{event_id}',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[EventResponse],
        )
def get_event(
    event_id: int,
    public_assistant: public_assistant_dependency,
    ) -> ApiResponse[EventResponse]:

    event_model = public_assistant.get_event(event_id)

    return ApiResponse[EventResponse].success(
        ApiInfo.EVENT_RETRIEVED,
        data=event_model,
        )
