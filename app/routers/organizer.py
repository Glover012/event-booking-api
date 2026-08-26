from fastapi import APIRouter, status

from ..api.pagination import Page
from ..dependencies import pagination_dependency
from ..api.response import ApiResponse
from ..api.info import ApiInfo
from ..schemas.events import CreateEventRequest, EventResponseOwner
from ..schemas.bookings import BookingStatusFilter, ParticipantResponse
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


@organizer_router.get(
        '/me/events',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[Page[EventResponseOwner]],
        )
def list_me_events(
    organizer_assistant: organizer_assistant_dependency,
    pagination: pagination_dependency,
    ) -> ApiResponse[Page[EventResponseOwner]]:

    page = organizer_assistant.list_me_events(pagination)

    return ApiResponse[Page[EventResponseOwner]].success(
        ApiInfo.ME_EVENTS_RETRIEVED,
        data=page,
        )


@organizer_router.get(
        '/events/{event_id}/participants',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[Page[ParticipantResponse]],
        )
def list_event_participants(
    event_id: int,
    organizer_assistant: organizer_assistant_dependency,
    pagination: pagination_dependency,
    booking_status: BookingStatusFilter = BookingStatusFilter.ALL,
    ) -> ApiResponse[Page[ParticipantResponse]]:
    # booking_status Query param, FastAPI assumes it itself
    page = organizer_assistant.list_event_participants(
        event_id,
        booking_status,
        pagination,
    )

    return ApiResponse[Page[ParticipantResponse]].success(
        ApiInfo.PARTICIPANTS_RETRIEVED,
        data=page,
        )
