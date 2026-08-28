from fastapi import APIRouter, status

from ..api.pagination import Page
from ..dependencies import pagination_dependency
from ..api.response import ApiResponse
from ..api.info import ApiInfo
from ..schemas.events import (
    ChangeEventStatusRequest,
    CreateEventRequest,
    EventResponseOwner,
    UpdateEventRequest,
)
from ..schemas.bookings import BookingStatusFilter, ParticipantResponse
from ..dependencies.assistants import organizer_assistant_dependency

### API Router ###
organizer_router = APIRouter(
    prefix="/organizer", 
    tags=["organizer"]
    )


### Endpoints - minimum role ORGANIZER ###
@organizer_router.get(
        '/events/{event_id}',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[EventResponseOwner],
        )
def get_me_event(
    event_id: int,
    organizer_assistant: organizer_assistant_dependency,
    ) -> ApiResponse[EventResponseOwner]:

    event_model = organizer_assistant.get_me_event(event_id)

    return ApiResponse[EventResponseOwner].success(
        ApiInfo.ME_EVENT_RETRIEVED,
        data=event_model,
        )


@organizer_router.get(
        '/events',
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


@organizer_router.post(
        '/events/create',
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


@organizer_router.put(
        '/events/{event_id}/status',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[EventResponseOwner],
        )
def change_event_status(
    event_id: int,
    organizer_assistant: organizer_assistant_dependency,
    change_status_request: ChangeEventStatusRequest,
    ) -> ApiResponse[EventResponseOwner]:

    event_model = organizer_assistant.change_event_status(
        event_id,
        change_status_request,
    )

    return ApiResponse[EventResponseOwner].success(
        ApiInfo.EVENT_STATUS_CHANGED,
        data=event_model,
        )


@organizer_router.post(
        '/events/{event_id}/publish',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[EventResponseOwner],
        )
def publish_event(
    event_id: int,
    organizer_assistant: organizer_assistant_dependency,
    ) -> ApiResponse[EventResponseOwner]:

    event_model = organizer_assistant.publish_event(event_id)

    return ApiResponse[EventResponseOwner].success(
        ApiInfo.EVENT_PUBLISHED,
        data=event_model,
        )


@organizer_router.put(
        '/events/{event_id}/update',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[EventResponseOwner],
        )
def update_event(
    event_id: int,
    organizer_assistant: organizer_assistant_dependency,
    update_event_request: UpdateEventRequest,
    ) -> ApiResponse[EventResponseOwner]:

    event_model = organizer_assistant.update_event(
        event_id,
        update_event_request,
    )

    return ApiResponse[EventResponseOwner].success(
        ApiInfo.EVENT_UPDATED,
        data=event_model,
        )


@organizer_router.post(
        '/events/{event_id}/cancel',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[EventResponseOwner],
        )
def cancel_event(
    event_id: int,
    organizer_assistant: organizer_assistant_dependency,
    ) -> ApiResponse[EventResponseOwner]:

    event_model = organizer_assistant.cancel_event(event_id)

    return ApiResponse[EventResponseOwner].success(
        ApiInfo.EVENT_CANCELLED,
        data=event_model,
        )


@organizer_router.delete(
        '/events/{event_id}/delete',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[None],
        )
def delete_event(
    event_id: int,
    organizer_assistant: organizer_assistant_dependency,
    ) -> ApiResponse[None]:

    organizer_assistant.delete_event(event_id)

    return ApiResponse[None].success(
        ApiInfo.EVENT_DELETED,
        )
