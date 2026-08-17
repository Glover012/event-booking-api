from fastapi import APIRouter, status

from ..dependencies import (
    organizer_assistant_dependency,
    event_service_dependency,
    pagination_dependency,
)
from ..api.response import ApiResponse
from ..api.pagination import Page
from ..api.info import ApiInfo
from ..schemas.events import CreateEventRequest, EventResponse

### API Router ###
event_router = APIRouter(
    prefix="/events",
    tags=["events"]
)


### Endpoints - Restricted to ORGANIZER ###
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

### Endpoints - Public ###
@event_router.get(
        '/',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[Page[EventResponse]],
        )
def list_events(
    event_service: event_service_dependency,
    pagination: pagination_dependency,
    ) -> ApiResponse[Page[EventResponse]]:

    models, total = event_service.list_public_models(
        limit=pagination.per_page,
        offset=pagination.offset,
    )

    return ApiResponse[Page[EventResponse]].success(
        ApiInfo.EVENTS_RETRIEVED,
        data=Page[EventResponse].create(
            items=models,
            total=total,
            pagination=pagination,
        ),
        )


@event_router.get(
        '/{event_id}',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[EventResponse],
        )
def get_event(
    event_id: int,
    event_service: event_service_dependency,
    ) -> ApiResponse[EventResponse]:

    event_model = event_service.get_public_model(event_id)

    return ApiResponse[EventResponse].success(
        ApiInfo.EVENT_RETRIEVED,
        data=event_model,
        )
