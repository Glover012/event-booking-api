from fastapi import APIRouter, status

from ..api.response import ApiResponse
from ..api.info import ApiInfo
from ..schemas.events import CreateEventRequest, EventResponseOwner
from ..dependencies.assistants import organizer_assistant_dependency

### API Router ###
organizer_router = APIRouter(tags=["organizer"])


### Endpoints - minimum role ORGANIZER ###
@organizer_router.post(
        '/events',
        status_code=status.HTTP_201_CREATED,
        response_model=ApiResponse[EventResponseOwner],
        )
def create_event(
    organizer_assistant: organizer_assistant_dependency,
    create_event_request: CreateEventRequest,
    ) -> ApiResponse[EventResponseOwner]:

    new_event = organizer_assistant.create_event(create_event_request)

    return ApiResponse[EventResponseOwner].success(
        ApiInfo.EVENT_CREATED,
        data=new_event,
        )
