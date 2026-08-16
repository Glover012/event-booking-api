from fastapi import APIRouter, status

from ..dependencies import organizer_assistant_dependency
from ..api.response import ApiResponse
from ..api.info import ApiInfo
from ..schemas.events import CreateEventRequest, EventResponse

### API Router ###
event_router = APIRouter(
    prefix="/events",
    tags=["events"]
)


### Endpoints ###
@event_router.post(
        '/',
        status_code=status.HTTP_201_CREATED,
        response_model=ApiResponse[EventResponse],
        )
def create_event(
    organizer_assistant: organizer_assistant_dependency,
    create_event_request: CreateEventRequest,
    ) -> ApiResponse[EventResponse]:

    new_event = organizer_assistant.create_event(create_event_request)

    return ApiResponse[EventResponse].success(
        ApiInfo.EVENT_CREATED,
        data=new_event,
        )
